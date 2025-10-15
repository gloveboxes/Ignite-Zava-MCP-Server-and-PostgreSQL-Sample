<template>
  <div class="ai-agent-page">
    <div class="container">
      <div class="page-header">
        <div class="header-left">
          <h1>🤖 AI Restocking Agent</h1>
          <p class="page-description">Intelligent inventory management powered by AI</p>
        </div>
        <div class="header-right">
          <router-link to="/management/inventory" class="btn btn-secondary">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="19" y1="12" x2="5" y2="12"/>
              <polyline points="12 19 5 12 12 5"/>
            </svg>
            Back to Inventory
          </router-link>
        </div>
      </div>

      <!-- Hero Section -->
      <div class="hero-section">
        <div class="hero-icon">🤖</div>
        <h2>AI-Powered Inventory Optimization</h2>
        <p class="hero-text">
          Our intelligent agent analyzes your inventory levels, sales patterns, supplier performance, 
          and market trends to provide data-driven restocking recommendations.
        </p>
      </div>

      <!-- Features Grid -->
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3>Smart Analytics</h3>
          <p>Analyze sales velocity, seasonal trends, and demand forecasting to optimize stock levels.</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">⚡</div>
          <h3>Priority Scoring</h3>
          <p>Automatically prioritize which items to restock first based on urgency and business impact.</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🎯</div>
          <h3>Supplier Matching</h3>
          <p>Match low-stock items with the best suppliers based on lead times, pricing, and ratings.</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">💰</div>
          <h3>Cost Optimization</h3>
          <p>Maximize bulk discounts and minimize ordering costs with intelligent batch recommendations.</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🌐</div>
          <h3>Multi-Store Balancing</h3>
          <p>Optimize inventory distribution across all your store locations for maximum efficiency.</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">📈</div>
          <h3>Predictive Insights</h3>
          <p>Predict future stockouts and overstock situations before they happen.</p>
        </div>
      </div>

      <!-- Coming Soon Box -->
      <div class="coming-soon-box">
        <div class="coming-soon-icon">🚀</div>
        <h3>Coming Soon!</h3>
        <p>
          We're building an advanced AI agent that will revolutionize how you manage inventory. 
          This feature will integrate with:
        </p>
        <ul>
          <li>Real-time inventory monitoring across all stores</li>
          <li>Historical sales data and trend analysis</li>
          <li>Supplier performance and availability data</li>
          <li>Automated purchase order generation</li>
          <li>Smart reordering with approval workflows</li>
          <li>Integration with existing procurement systems</li>
        </ul>
        <p class="notify-text">
          Want to be notified when this launches? Contact your account manager!
        </p>
      </div>

      <!-- Demo Preview -->
      <div class="demo-section">
        <h3>What to Expect</h3>
        <div class="demo-preview">
          <div class="demo-item">
            <span class="demo-number">1</span>
            <div class="demo-content">
              <strong>Chat with the AI Agent</strong>
              <p>Ask questions like "Which items should I restock first?" or "Show me low stock items with fast-moving suppliers"</p>
            </div>
          </div>
          
          <div class="demo-item">
            <span class="demo-number">2</span>
            <div class="demo-content">
              <strong>Get Intelligent Recommendations</strong>
              <p>Receive prioritized restocking lists with detailed reasoning and cost analysis</p>
            </div>
          </div>
          
          <div class="demo-item">
            <span class="demo-number">3</span>
            <div class="demo-content">
              <strong>Execute with One Click</strong>
              <p>Approve recommendations and automatically generate purchase orders for suppliers</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AIAgentPage',
  mounted() {
    console.log('AI Agent page loaded - Feature coming soon!');
  }
};
</script>

<style scoped>
.ai-agent-page {
  padding-bottom: 4rem;
}

.ai-agent-page .container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.header-left h1 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: var(--primary-color);
}

.page-description {
  color: var(--secondary-color);
  font-size: 0.95rem;
}

.header-right .btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Hero Section */
.hero-section {
  text-align: center;
  padding: 4rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
  margin-bottom: 3rem;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.hero-icon {
  font-size: 5rem;
  margin-bottom: 1.5rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.hero-section h2 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.hero-text {
  font-size: 1.125rem;
  max-width: 700px;
  margin: 0 auto;
  opacity: 0.95;
  line-height: 1.7;
}

/* Features Grid */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.75rem;
}

.feature-card p {
  color: var(--secondary-color);
  line-height: 1.6;
}

/* Coming Soon Box */
.coming-soon-box {
  background: white;
  padding: 3rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 3rem;
  border: 2px dashed #d0d7de;
}

.coming-soon-icon {
  font-size: 4rem;
  text-align: center;
  margin-bottom: 1rem;
}

.coming-soon-box h3 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
  text-align: center;
  margin-bottom: 1rem;
}

.coming-soon-box > p {
  font-size: 1.125rem;
  color: var(--secondary-color);
  text-align: center;
  margin-bottom: 2rem;
  line-height: 1.7;
}

.coming-soon-box ul {
  max-width: 600px;
  margin: 0 auto 2rem;
  list-style: none;
  padding: 0;
}

.coming-soon-box li {
  padding: 0.75rem 0;
  padding-left: 2rem;
  position: relative;
  color: var(--primary-color);
  font-weight: 500;
}

.coming-soon-box li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: var(--accent-color);
  font-weight: 700;
  font-size: 1.25rem;
}

.notify-text {
  text-align: center;
  font-style: italic;
  color: var(--secondary-color);
  margin-top: 2rem;
}

/* Demo Section */
.demo-section {
  background: white;
  padding: 3rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.demo-section h3 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--primary-color);
  text-align: center;
  margin-bottom: 2rem;
}

.demo-preview {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.demo-item {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

.demo-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  font-size: 1.5rem;
  font-weight: 700;
  flex-shrink: 0;
}

.demo-content {
  flex: 1;
}

.demo-content strong {
  display: block;
  font-size: 1.25rem;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.demo-content p {
  color: var(--secondary-color);
  line-height: 1.6;
}

/* Responsive */
@media (max-width: 768px) {
  .ai-agent-page .container {
    padding: 0 1rem;
  }
  
  .hero-section {
    padding: 3rem 1.5rem;
  }
  
  .hero-icon {
    font-size: 3.5rem;
  }
  
  .hero-section h2 {
    font-size: 1.75rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .coming-soon-box {
    padding: 2rem 1.5rem;
  }
  
  .demo-section {
    padding: 2rem 1.5rem;
  }
  
  .demo-item {
    flex-direction: column;
    text-align: center;
  }
  
  .demo-number {
    margin: 0 auto;
  }
}
</style>
