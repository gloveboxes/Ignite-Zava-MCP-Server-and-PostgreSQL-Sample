<template>
  <div class="ai-agent-page">
    <!-- Header -->
    <div class="page-header">
      <router-link to="/management/inventory" class="back-link">
        <i class="bi bi-arrow-left"></i> Back to Inventory
      </router-link>
      <h1><i class="bi bi-robot"></i> AI Restocking Agent</h1>
      <p class="subtitle">Analyze inventory levels and get intelligent restocking recommendations</p>
    </div>

    <!-- Main Content -->
    <div class="agent-container">
      <!-- Hero Section -->
      <div class="hero-section" v-if="!isRunning && !hasCompleted">
        <div class="hero-content">
          <i class="bi bi-lightbulb hero-icon"></i>
          <h2>Intelligent Inventory Analysis</h2>
          <p>
            Our AI agent analyzes your inventory across all stores, identifies low-stock items,
            and provides prioritized restocking recommendations based on company policies and budget constraints.
          </p>
          <div class="features">
            <div class="feature">
              <i class="bi bi-check-circle-fill"></i>
              <span>Real-time inventory analysis</span>
            </div>
            <div class="feature">
              <i class="bi bi-check-circle-fill"></i>
              <span>Policy-aware recommendations</span>
            </div>
            <div class="feature">
              <i class="bi bi-check-circle-fill"></i>
              <span>Budget optimization</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Section -->
      <div class="input-section" v-if="!isRunning && !hasCompleted">
        <label for="instructions" class="input-label">
          <i class="bi bi-chat-left-text"></i> Instructions for AI Agent
        </label>
        <textarea
          id="instructions"
          v-model="userInstructions"
          class="instructions-input"
          rows="4"
          placeholder="Enter your instructions for the AI agent..."
        ></textarea>
        <button @click="startAnalysis" class="launch-button" :disabled="!userInstructions.trim()">
          <i class="bi bi-rocket-takeoff"></i> Launch AI Analysis
        </button>
      </div>

      <!-- Progress Section with Steps -->
      <div class="progress-section" v-if="isRunning || events.length > 0">
        <div class="progress-card">
          <!-- Progress Header -->
          <div class="progress-header">
            <div class="header-left">
              <div class="spinner" v-if="isRunning"></div>
              <i class="bi bi-x-circle-fill error-icon" v-else-if="error"></i>
              <i class="bi bi-check-circle-fill complete-icon" v-else></i>
              <div>
                <h3>{{ error ? 'Analysis Failed' : (isRunning ? 'AI Analysis in Progress' : 'Analysis Complete') }}</h3>
                <p class="progress-subtitle">{{ progressSummary }}</p>
              </div>
            </div>
            <button 
              v-if="events.length > 0" 
              @click="showDetails = !showDetails" 
              class="details-toggle"
            >
              <i :class="showDetails ? 'bi bi-chevron-up' : 'bi bi-chevron-down'"></i>
              {{ showDetails ? 'Hide Details' : 'Show Details' }}
            </button>
          </div>

          <!-- Progress Steps (always visible) -->
          <div class="progress-steps">
            <div 
              v-for="step in progressSteps" 
              :key="step.id"
              class="progress-step"
              :class="{ 
                'active': step.status === 'active', 
                'complete': step.status === 'complete',
                'pending': step.status === 'pending',
                'error': step.status === 'error'
              }"
            >
              <div class="step-indicator">
                <div class="spinner-small" v-if="step.status === 'active'"></div>
                <i class="bi bi-check-circle-fill" v-else-if="step.status === 'complete'"></i>
                <i class="bi bi-x-circle-fill" v-else-if="step.status === 'error'"></i>
                <i class="bi bi-circle" v-else></i>
              </div>
              <div class="step-content">
                <div class="step-title">{{ step.title }}</div>
                <div class="step-description" v-if="step.description">{{ step.description }}</div>
              </div>
            </div>
          </div>

          <!-- Detailed Events (collapsible) -->
          <transition name="slide">
            <div class="events-details" v-if="showDetails && events.length > 0">
              <div class="details-header">
                <i class="bi bi-list-ul"></i>
                <span>Detailed Activity Log</span>
              </div>
              <div class="events-container">
                <div 
                  v-for="(event, index) in events" 
                  :key="index" 
                  class="event-item"
                  :class="{ 'fade-in': index === events.length - 1 }"
                >
                  <div class="event-bullet"></div>
                  <div class="event-details">
                    <div class="event-content">{{ event.message }}</div>
                    <div class="event-time">{{ formatTime(event.timestamp) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- Final Output -->
      <div class="output-section" v-if="finalOutput">
        <div class="output-header">
          <i class="bi bi-check-circle-fill success-icon"></i>
          <h3>Analysis Complete</h3>
        </div>
        <div class="output-content markdown-content" v-html="renderedMarkdown"></div>
        <button @click="resetAnalysis" class="reset-button">
          <i class="bi bi-arrow-counterclockwise"></i> Run Another Analysis
        </button>
      </div>

      <!-- Error Display -->
      <div class="error-section" v-if="error">
        <div class="error-header">
          <i class="bi bi-exclamation-triangle-fill"></i>
          <h3>Error Occurred</h3>
        </div>
        <div class="error-content">{{ error }}</div>
        <button @click="resetAnalysis" class="retry-button">
          <i class="bi bi-arrow-clockwise"></i> Try Again
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { marked } from 'marked'

// Configure marked options
marked.setOptions({
  breaks: true,
  gfm: true
})

// State
const userInstructions = ref('Analyze inventory and recommend restocking priorities')
const isRunning = ref(false)
const hasCompleted = ref(false)
const events = ref([])
const finalOutput = ref(null)
const error = ref(null)
const showDetails = ref(false)
const currentStep = ref(0)
let ws = null

// Progress steps
const progressSteps = ref([
  { id: 1, title: 'Starting Analysis', description: '', status: 'pending' },
  { id: 2, title: 'Analyzing Inventory', description: '', status: 'pending' },
  { id: 3, title: 'Checking Policies', description: '', status: 'pending' },
  { id: 4, title: 'Generating Recommendations', description: '', status: 'pending' }
])

// Progress summary
const progressSummary = computed(() => {
  if (error.value) {
    return 'Analysis failed - please review the error below'
  }
  if (!isRunning.value && hasCompleted.value) {
    return `Analysis completed successfully with ${events.value.length} events processed`
  }
  const activeStep = progressSteps.value.find(s => s.status === 'active')
  return activeStep ? activeStep.title : 'Connecting to AI Agent...'
})

// Render markdown output
const renderedMarkdown = computed(() => {
  if (!finalOutput.value) return ''
  try {
    return marked.parse(finalOutput.value)
  } catch (err) {
    console.error('Error rendering markdown:', err)
    return `<pre>${finalOutput.value}</pre>`
  }
})

// Start analysis
const startAnalysis = () => {
  // Reset state
  events.value = []
  finalOutput.value = null
  error.value = null
  isRunning.value = true
  hasCompleted.value = false
  showDetails.value = false
  currentStep.value = 0
  
  // Reset progress steps
  progressSteps.value.forEach(step => {
    step.status = 'pending'
    step.description = ''
  })

  // Connect to WebSocket
  const wsUrl = 'ws://localhost:8091/ws/ai-agent/inventory'
  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    addEvent('Connected to AI Agent')
    updateStep(0, 'active', 'Connecting to AI Agent')
    // Send the user instructions
    ws.send(JSON.stringify({
      request: userInstructions.value
    }))
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      
      if (data.type === 'started') {
        addEvent('AI Agent workflow started')
        updateStep(0, 'complete', 'Connected successfully')
        updateStep(1, 'active', 'Processing inventory data')
      } else if (data.type === 'event') {
        // Display the event
        addEvent(data.event)
        // Update steps based on event content
        updateStepsFromEvent(data.event)
      } else if (data.type === 'completed') {
        addEvent('Analysis completed successfully')
        finalOutput.value = data.output
        // Complete all steps
        progressSteps.value.forEach(step => {
          if (step.status !== 'complete') {
            step.status = 'complete'
          }
        })
        isRunning.value = false
        hasCompleted.value = true
        ws.close()
      } else if (data.type === 'error') {
        // Handle error - support both 'error' and 'message' fields
        const errorMessage = data.error || data.message || 'An unknown error occurred'
        addEvent(`Error: ${errorMessage}`)
        error.value = errorMessage
        isRunning.value = false
        hasCompleted.value = false
        // Mark current active step as failed
        const activeStep = progressSteps.value.find(s => s.status === 'active')
        if (activeStep) {
          activeStep.status = 'error'
          activeStep.description = 'Failed'
        }
        ws.close()
      }
    } catch (err) {
      console.error('Failed to parse WebSocket message:', err)
      const errorMsg = 'Failed to process server response'
      addEvent(errorMsg)
      error.value = errorMsg
      isRunning.value = false
    }
  }

  ws.onerror = (err) => {
    console.error('WebSocket error:', err)
    error.value = 'Failed to connect to AI Agent. Please ensure the backend is running.'
    isRunning.value = false
  }

  ws.onclose = () => {
    if (isRunning.value) {
      addEvent('Connection closed')
      isRunning.value = false
    }
  }
}

// Update step status
const updateStep = (stepIndex, status, description = '') => {
  if (stepIndex >= 0 && stepIndex < progressSteps.value.length) {
    progressSteps.value[stepIndex].status = status
    if (description) {
      progressSteps.value[stepIndex].description = description
    }
  }
}

// Update steps based on event content
const updateStepsFromEvent = (eventMessage) => {
  const msg = eventMessage.toLowerCase()
  
  // Analyzing inventory
  if (msg.includes('inventory') || msg.includes('stock') || msg.includes('department')) {
    if (progressSteps.value[1].status !== 'complete') {
      updateStep(1, 'active', 'Analyzing stock levels across stores')
    }
  }
  
  // Checking policies
  if (msg.includes('policy') || msg.includes('policies') || msg.includes('budget')) {
    updateStep(1, 'complete', 'Inventory analysis complete')
    updateStep(2, 'active', 'Reviewing company policies and budgets')
  }
  
  // Generating recommendations
  if (msg.includes('recommend') || msg.includes('summary') || msg.includes('priorit')) {
    updateStep(2, 'complete', 'Policy check complete')
    updateStep(3, 'active', 'Preparing restocking recommendations')
  }
}

// Add event to the list
const addEvent = (message) => {
  events.value.push({
    message,
    timestamp: new Date()
  })
}

// Format timestamp
const formatTime = (date) => {
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  })
}

// Reset analysis
const resetAnalysis = () => {
  events.value = []
  finalOutput.value = null
  error.value = null
  isRunning.value = false
  hasCompleted.value = false
  showDetails.value = false
  currentStep.value = 0
  progressSteps.value.forEach(step => {
    step.status = 'pending'
    step.description = ''
  })
  if (ws) {
    ws.close()
    ws = null
  }
}
</script>

<style scoped>
.ai-agent-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #6c757d;
  text-decoration: none;
  margin-bottom: 1rem;
  font-size: 0.95rem;
  transition: color 0.2s;
}

.back-link:hover {
  color: #495057;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #212529;
  margin-bottom: 0.5rem;
}

.page-header h1 i {
  color: #0d6efd;
  margin-right: 0.5rem;
}

.subtitle {
  color: #6c757d;
  font-size: 1.1rem;
}

.agent-container {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Hero Section */
.hero-section {
  text-align: center;
  padding: 2rem 0;
  border-bottom: 1px solid #e9ecef;
  margin-bottom: 2rem;
}

.hero-content {
  max-width: 700px;
  margin: 0 auto;
}

.hero-icon {
  font-size: 4rem;
  color: #ffc107;
  margin-bottom: 1rem;
}

.hero-section h2 {
  font-size: 1.75rem;
  font-weight: 600;
  color: #212529;
  margin-bottom: 1rem;
}

.hero-section p {
  color: #6c757d;
  font-size: 1.05rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.features {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.feature {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #28a745;
  font-weight: 500;
}

.feature i {
  font-size: 1.2rem;
}

/* Input Section */
.input-section {
  max-width: 800px;
  margin: 0 auto;
}

.input-label {
  display: block;
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.75rem;
  font-size: 1.05rem;
}

.input-label i {
  color: #0d6efd;
}

.instructions-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s;
}

.instructions-input:focus {
  outline: none;
  border-color: #0d6efd;
}

.launch-button {
  margin-top: 1.5rem;
  width: 100%;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.launch-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3);
}

.launch-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.launch-button i {
  font-size: 1.2rem;
}

/* Progress Section */
.progress-section {
  margin-top: 2rem;
}

.progress-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e9ecef;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #e9ecef;
}

.header-left {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.progress-header h3 {
  color: #212529;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.progress-subtitle {
  color: #6c757d;
  font-size: 0.95rem;
  margin: 0;
}

.spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 4px solid #e9ecef;
  border-top-color: #0d6efd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  flex-shrink: 0;
}

.spinner-small {
  width: 1.25rem;
  height: 1.25rem;
  border: 3px solid #e9ecef;
  border-top-color: #0d6efd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.complete-icon {
  font-size: 2.5rem;
  color: #28a745;
  flex-shrink: 0;
}

.error-icon {
  font-size: 2.5rem;
  color: #dc3545;
  flex-shrink: 0;
}

.details-toggle {
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  color: #495057;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}

.details-toggle:hover {
  background: #e9ecef;
  border-color: #ced4da;
}

/* Progress Steps */
.progress-steps {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.progress-step {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  position: relative;
}

.progress-step:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 0.75rem;
  top: 2rem;
  width: 2px;
  height: calc(100% + 1rem);
  background: #e9ecef;
}

.progress-step.complete:not(:last-child)::before {
  background: #28a745;
}

.progress-step.active:not(:last-child)::before {
  background: linear-gradient(to bottom, #28a745 50%, #e9ecef 50%);
}

.progress-step.error:not(:last-child)::before {
  background: linear-gradient(to bottom, #28a745 50%, #dc3545 50%);
}

.step-indicator {
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.step-indicator i {
  font-size: 1.5rem;
}

.progress-step.pending .step-indicator i {
  color: #dee2e6;
}

.progress-step.active .step-indicator i {
  color: #0d6efd;
}

.progress-step.complete .step-indicator i {
  color: #28a745;
}

.progress-step.error .step-indicator i {
  color: #dc3545;
}

.step-content {
  flex: 1;
  padding-top: 0.15rem;
}

.step-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: #212529;
  margin-bottom: 0.25rem;
}

.progress-step.pending .step-title {
  color: #adb5bd;
}

.progress-step.error .step-title {
  color: #dc3545;
}

.step-description {
  font-size: 0.9rem;
  color: #6c757d;
  font-style: italic;
}

.progress-step.error .step-description {
  color: #dc3545;
  font-weight: 500;
}

/* Events Details */
.events-details {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e9ecef;
}

.details-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 1rem;
  font-size: 1rem;
}

.details-header i {
  color: #0d6efd;
}

.events-container {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}

.event-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #e9ecef;
}

.event-item:last-child {
  border-bottom: none;
}

.event-item.fade-in {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.event-bullet {
  width: 6px;
  height: 6px;
  background: #0d6efd;
  border-radius: 50%;
  margin-top: 0.5rem;
  flex-shrink: 0;
}

.event-details {
  flex: 1;
}

.event-content {
  color: #212529;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.event-time {
  font-size: 0.8rem;
  color: #868e96;
}

/* Slide transition */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
}

/* Output Section */
.output-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e9ecef;
}

.output-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.success-icon {
  font-size: 2rem;
  color: #28a745;
}

.output-header h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #28a745;
}

.output-content {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

/* Markdown Content Styling */
.markdown-content {
  color: #212529;
  line-height: 1.7;
}

.markdown-content h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #212529;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #dee2e6;
}

.markdown-content h1:first-child {
  margin-top: 0;
}

.markdown-content h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #495057;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.markdown-content h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #495057;
  margin-top: 1.25rem;
  margin-bottom: 0.75rem;
}

.markdown-content p {
  margin-bottom: 1rem;
}

.markdown-content ul,
.markdown-content ol {
  margin-bottom: 1rem;
  padding-left: 2rem;
}

.markdown-content li {
  margin-bottom: 0.5rem;
}

.markdown-content strong {
  font-weight: 600;
  color: #212529;
}

.markdown-content em {
  font-style: italic;
  color: #495057;
}

.markdown-content code {
  background: #e9ecef;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
  color: #d63384;
}

.markdown-content pre {
  background: #2d2d2d;
  color: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
  margin-bottom: 1rem;
}

.markdown-content pre code {
  background: transparent;
  color: inherit;
  padding: 0;
  font-size: 0.9rem;
}

.markdown-content blockquote {
  border-left: 4px solid #0d6efd;
  padding-left: 1rem;
  margin: 1rem 0;
  color: #6c757d;
  font-style: italic;
}

.markdown-content table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.markdown-content th,
.markdown-content td {
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  text-align: left;
}

.markdown-content th {
  background: #e9ecef;
  font-weight: 600;
}

.markdown-content tr:nth-child(even) {
  background: #f8f9fa;
}

.markdown-content a {
  color: #0d6efd;
  text-decoration: none;
}

.markdown-content a:hover {
  text-decoration: underline;
}

.markdown-content hr {
  border: none;
  border-top: 1px solid #dee2e6;
  margin: 1.5rem 0;
}

.reset-button {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  background: #28a745;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.reset-button:hover {
  background: #218838;
}

/* Error Section */
.error-section {
  margin-top: 2rem;
  padding: 2rem;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 8px;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.error-header i {
  font-size: 2rem;
  color: #dc3545;
}

.error-header h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #dc3545;
}

.error-content {
  color: #856404;
  font-size: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: white;
  border-radius: 4px;
}

.retry-button {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  background: #dc3545;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.retry-button:hover {
  background: #c82333;
}

/* Responsive */
@media (max-width: 768px) {
  .ai-agent-page {
    padding: 1rem;
  }

  .agent-container {
    padding: 1.5rem;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .hero-section h2 {
    font-size: 1.5rem;
  }

  .features {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
