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

      <!-- Progress Section -->
      <div class="progress-section" v-if="isRunning">
        <div class="progress-header">
          <div class="spinner"></div>
          <h3>Analysis in Progress...</h3>
        </div>
        <p class="progress-subtitle">The AI agent is analyzing your inventory. This may take a moment.</p>
      </div>

      <!-- Events Display -->
      <div class="events-section" v-if="events.length > 0">
        <h3><i class="bi bi-activity"></i> Live Activity Stream</h3>
        <div class="events-container">
          <div 
            v-for="(event, index) in events" 
            :key="index" 
            class="event-item"
            :class="{ 'fade-in': index === events.length - 1 }"
          >
            <div class="event-time">{{ formatTime(event.timestamp) }}</div>
            <div class="event-content">{{ event.message }}</div>
          </div>
        </div>
      </div>

      <!-- Final Output -->
      <div class="output-section" v-if="finalOutput">
        <div class="output-header">
          <i class="bi bi-check-circle-fill success-icon"></i>
          <h3>Analysis Complete</h3>
        </div>
        <div class="output-content">
          <pre>{{ finalOutput }}</pre>
        </div>
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
import { ref } from 'vue'

// State
const userInstructions = ref('Analyze inventory and recommend restocking priorities')
const isRunning = ref(false)
const hasCompleted = ref(false)
const events = ref([])
const finalOutput = ref(null)
const error = ref(null)
let ws = null

// Start analysis
const startAnalysis = () => {
  // Reset state
  events.value = []
  finalOutput.value = null
  error.value = null
  isRunning.value = true
  hasCompleted.value = false

  // Connect to WebSocket
  const wsUrl = 'ws://localhost:8091/ws/ai-agent/inventory'
  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    addEvent('Connected to AI Agent')
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
      } else if (data.type === 'event') {
        // Display the event
        addEvent(data.event)
      } else if (data.type === 'completed') {
        addEvent('Analysis completed successfully')
        finalOutput.value = data.output
        isRunning.value = false
        hasCompleted.value = true
        ws.close()
      } else if (data.type === 'error') {
        error.value = data.error
        isRunning.value = false
        ws.close()
      }
    } catch (err) {
      console.error('Failed to parse WebSocket message:', err)
      addEvent(`Received: ${event.data}`)
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
  text-align: center;
  padding: 3rem 0;
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 4px solid #e9ecef;
  border-top-color: #0d6efd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.progress-section h3 {
  color: #0d6efd;
  font-size: 1.5rem;
  font-weight: 600;
}

.progress-subtitle {
  color: #6c757d;
  font-size: 1.05rem;
}

/* Events Section */
.events-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e9ecef;
}

.events-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 1rem;
}

.events-section h3 i {
  color: #0d6efd;
  margin-right: 0.5rem;
}

.events-container {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}

.event-item {
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background: white;
  border-left: 3px solid #0d6efd;
  border-radius: 4px;
}

.event-item:last-child {
  margin-bottom: 0;
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

.event-time {
  font-size: 0.85rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.event-content {
  color: #212529;
  font-size: 0.95rem;
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

.output-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  font-size: 0.95rem;
  color: #212529;
  line-height: 1.6;
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
