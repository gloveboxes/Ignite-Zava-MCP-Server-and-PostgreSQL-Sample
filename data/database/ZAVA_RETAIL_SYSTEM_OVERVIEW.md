# Zava Retail System - Complete Overview

**Last Updated**: October 10, 2025  
**Database**: PostgreSQL with pgvector extension  
**Total Products**: 129 SKUs across 5 main categories  
**Store Count**: 7 popup stores + 1 online store  
**Region**: Washington State, USA

---

## Table of Contents
1. [Product Catalog](#product-catalog)
2. [Store Network](#store-network)
3. [Store Product Assignments](#store-product-assignments)
4. [Seasonal Inventory Management](#seasonal-inventory-management)
5. [Supplier Network](#supplier-network)
6. [Company Policies](#company-policies)
7. [Procurement & Authorization](#procurement--authorization)

---

## Product Catalog

### Overview
- **Total Products**: 129 SKUs
- **Main Categories**: 5
- **Product Types**: 21
- **Price Range**: $9.99 - $149.99
- **All Products**: Washington State seasonal patterns applied

### Category Breakdown

#### 1. Apparel - Tops (45 products)
**Seasonal Pattern**: Summer peak (April-August, 1.4x multiplier)
- **T-Shirts** (12 SKUs): $15.99 - $28.99
  - Classic Cotton, V-Neck, Graphic Print, Long Sleeve, Striped, Polo Style, Pocket, Athletic, Henley, Raglan, Scoop Neck, Thermal Waffle
- **Formal Shirts** (8 SKUs): $38.99 - $54.99
  - Oxford Button-Down, Slim Fit, Wrinkle-Free, French Cuff, Striped, Classic White, Chambray, Flannel Button-Down
- **Hoodies** (7 SKUs): $34.99 - $54.99
  - Pullover Fleece, Zip-Up, Athletic Performance, Oversized Comfort, Logo Print, Sherpa Lined, Tech Fleece
- **Sweatshirts** (4 SKUs): $29.99 - $38.99
  - Crewneck, Vintage College, Quarter-Zip, Mock Neck
- **Flannel Shirts** (4 SKUs): $39.99 - $54.99
  - Classic Plaid, Heavyweight Work, Slim Fit, Flannel Shirt Jacket

#### 2. Apparel - Bottoms (21 products)
**Seasonal Pattern**: Stable year-round (1.0x multiplier)
- **Jeans** (9 SKUs): $48.99 - $79.99
  - Straight Leg, Slim Fit Stretch, Bootcut, Distressed, Dark Wash, Relaxed Fit, Skinny Fit, Raw Selvedge, High-Waist Mom
- **Pants** (4 SKUs): $39.99 - $52.99
  - Chino, Cargo Utility, Jogger Sweatpants, Corduroy
- **Shorts** (4 SKUs): $24.99 - $36.99
  - Casual Chino, Athletic Running, Cargo, Denim

#### 3. Outerwear (14 products)
**Seasonal Pattern**: Winter peak (December-January, 1.8x multiplier)
- **Jackets** (10 SKUs): $44.99 - $149.99
  - Denim Classic, Windbreaker Sport, Bomber, Leather (Faux), Puffer, Rain Waterproof, Fleece Zip, Down Parka, Softshell, Quilted Vest
- **Coats** (4 SKUs): $89.99 - $139.99
  - Peacoat Wool Blend, Trench Coat, Parka Winter, Rain Coat Long

#### 4. Footwear (26 products)
**Seasonal Pattern**: Summer peak (July, 1.4x multiplier)
- **Sneakers** (9 SKUs): $44.99 - $89.99
  - Classic White, Running Athletic, High-Top, Slip-On Canvas, Retro Style, Mesh Athletic, Platform, Trail Running, Skate Shoes
- **Boots** (5 SKUs): $49.99 - $119.99
  - Waterproof Hiking, Chelsea Ankle, Combat, Rain Waterproof, Work Steel Toe
- **Dress Shoes** (5 SKUs): $79.99 - $99.99
  - Oxford Leather, Loafer Slip-On, Derby, Monk Strap, Brogue Wingtip
- **Sandals** (3 SKUs): $19.99 - $39.99
  - Sport Sandals, Flip Flops, Slide Sandals

#### 5. Accessories (43 products)
**Seasonal Pattern**: Winter peak (December, 1.3x multiplier)
- **Caps & Hats** (8 SKUs): $14.99 - $34.99
  - Baseball Cap, Snapback, Beanie Winter, Bucket Hat, Trucker Cap, Fedora, Knit Pom Beanie, Fleece Ear Warmer
- **Socks** (8 SKUs): $9.99 - $19.99
  - Athletic Crew Pack, No-Show Ankle, Dress Set, Compression Athletic, Thermal Winter, Casual Cotton, Wool Hiking, Cozy Slipper
- **Backpacks & Bags** (9 SKUs): $24.99 - $79.99
  - School Backpack, Laptop Commuter, Hiking Daypack, Mini Fashion, Rolling Travel, Sports Gym, Canvas Tote, Waterproof Dry Bag, Crossbody Sling
- **Gloves** (4 SKUs): $12.99 - $29.99
  - Winter Knit, Touchscreen, Waterproof Winter, Fleece Liner
- **Scarves** (4 SKUs): $14.99 - $39.99
  - Cashmere Blend, Infinity Loop, Plaid Winter, Fleece Neck Gaiter
- **Belts** (4 SKUs): $19.99 - $34.99
  - Leather Dress, Canvas Web, Reversible, Braided Leather
- **Sunglasses** (4 SKUs): $39.99 - $49.99
  - Classic Aviator, Wayfarer, Sport Wrap, Round Frame

---

## Store Network

### Store Locations

#### 🏙️ Flagship Store
**Zava Pop-Up Pike Place** (Seattle)
- **Location**: Downtown Seattle, Pike Place Market area
- **Customer Base**: 30% of total (23.1% actual)
- **Order Frequency**: 3.0x baseline
- **Order Value**: 1.3x baseline
- **Products Carried**: 52 SKUs
- **Theme**: Urban Trendy - Streetwear & Everyday Essentials

#### 💼 Premium Mall Location
**Zava Pop-Up Bellevue Square** (Bellevue)
- **Location**: Upscale Bellevue Square Mall
- **Customer Base**: 25% of total (19.0% actual)
- **Order Frequency**: 2.6x baseline
- **Order Value**: 1.2x baseline
- **Products Carried**: 47 SKUs
- **Theme**: Business Casual Premium - Professional Wear

#### 👨‍👩‍👧‍👦 Family-Oriented Location
**Zava Pop-Up Tacoma Mall** (Tacoma)
- **Location**: South Sound regional mall
- **Customer Base**: 20% of total (15.6% actual)
- **Order Frequency**: 2.4x baseline
- **Order Value**: 1.1x baseline
- **Products Carried**: 50 SKUs
- **Theme**: Family Casual - Practical & Affordable

#### 🏔️ Eastern Washington Location
**Zava Pop-Up Spokane Pavilion** (Spokane)
- **Location**: Eastern Washington shopping center
- **Customer Base**: 8% of total (6.1% actual)
- **Order Frequency**: 2.0x baseline
- **Order Value**: 1.0x baseline
- **Products Carried**: 52 SKUs
- **Theme**: Outdoor Adventure - Hiking & Rugged Wear

#### 🏃 Transit Hub Location
**Zava Pop-Up Everett Station** (Everett)
- **Location**: Major transit station
- **Customer Base**: 7% of total (5.4% actual)
- **Order Frequency**: 1.8x baseline
- **Order Value**: 0.95x baseline
- **Products Carried**: 47 SKUs
- **Theme**: Commuter Essentials - Work Wear & Travel

#### 💻 Tech Corridor Location
**Zava Pop-Up Redmond Town Center** (Redmond)
- **Location**: Tech hub shopping center
- **Customer Base**: 6% of total (4.6% actual)
- **Order Frequency**: 1.6x baseline
- **Order Value**: 0.9x baseline
- **Products Carried**: 45 SKUs
- **Theme**: Tech Casual - Smart Casual & Athleisure

#### 🌊 Waterfront Boutique
**Zava Pop-Up Kirkland Waterfront** (Kirkland)
- **Location**: Upscale waterfront district
- **Customer Base**: 4% of total (3.1% actual)
- **Order Frequency**: 1.4x baseline
- **Order Value**: 0.85x baseline
- **Products Carried**: 54 SKUs
- **Theme**: Lifestyle Boutique - Curated Fashion

#### 🌐 E-Commerce Platform
**Zava Online Store**
- **Location**: Online only
- **Customer Base**: 30% of total (23.0% actual)
- **Order Frequency**: 3.0x baseline
- **Order Value**: 1.5x baseline
- **Products Carried**: 129 SKUs (all products)
- **Theme**: Full Catalog

### Store Statistics
- **Average Popup Size**: ~48 products
- **Product Overlap**: 20-30% shared essentials
- **Unique Assortment**: 70-80% per store
- **Total Customers**: 50,000 across all stores

---

## Store Product Assignments

### Configuration-Based Distribution
Product assignments are managed via `store_products.json` for **reproducibility**. Each store has a curated selection matching its theme and customer demographics.

### Pike Place (52 products)
**Focus**: Urban streetwear, trendy casuals
- **Tops**: Classic tees, hoodies, casual flannels
- **Bottoms**: Trendy jeans (slim, skinny, distressed), joggers
- **Outerwear**: Denim, windbreaker, rain jackets, fleece
- **Footwear**: Sneakers (classic white, high-tops, retro), Chelsea boots, sandals
- **Accessories**: Baseball caps, snapbacks, backpacks, sunglasses

### Bellevue Square (47 products)
**Focus**: Business casual, premium professional
- **Tops**: Formal shirts (Oxford, slim fit, French cuff), polo tees
- **Bottoms**: Premium jeans (dark wash, raw selvedge), chinos, corduroy
- **Outerwear**: Peacoat, trench coat, bomber jacket
- **Footwear**: Dress shoes (all 5 types), quality sneakers
- **Accessories**: Leather belts, dress socks, laptop backpack

### Tacoma Mall (50 products)
**Focus**: Family-friendly basics and practical wear
- **Tops**: Basic tees, flannel shirts, comfortable hoodies
- **Bottoms**: Classic jeans, chinos, cargo pants, all shorts
- **Outerwear**: Practical jackets (rain, fleece, puffer), long rain coat
- **Footwear**: Versatile sneakers, hiking boots, work boots
- **Accessories**: Beanies, basic socks, school backpacks, gloves

### Spokane Pavilion (52 products)
**Focus**: Outdoor adventure, cold weather gear
- **Tops**: Thermal tees, athletic performance, heavy flannels
- **Bottoms**: Durable jeans, cargo pants
- **Outerwear**: Full jacket selection (puffer, down parka, softshell), winter coats
- **Footwear**: Hiking boots, trail running shoes, work boots
- **Accessories**: Winter gear (beanies, gloves, scarves), hiking backpacks

### Everett Station (47 products)
**Focus**: Commuter-friendly, work-appropriate
- **Tops**: Business shirts, polo tees, practical tees
- **Bottoms**: Business casual jeans and chinos, joggers
- **Outerwear**: Commuter jackets (rain, softshell), long rain coat
- **Footwear**: Work-appropriate sneakers, dress shoes, Chelsea boots
- **Accessories**: Commuter backpacks, belts, travel bags

### Redmond Town Center (45 products)
**Focus**: Tech casual, modern athleisure
- **Tops**: Modern tees, tech hoodies, slim fit shirts
- **Bottoms**: Slim jeans, chinos, athletic joggers
- **Outerwear**: Tech-friendly jackets (bomber, fleece, softshell)
- **Footwear**: Athletic sneakers, casual dress shoes
- **Accessories**: Tech backpacks, athletic socks, modern caps

### Kirkland Waterfront (54 products)
**Focus**: Lifestyle boutique, premium casual
- **Tops**: Fashion tees (Henley, raglan, scoop), premium shirts
- **Bottoms**: Fashion jeans (skinny, high-waist mom), corduroy
- **Outerwear**: Style jackets (leather, bomber, denim), peacoat, trench
- **Footwear**: Fashion sneakers, premium dress shoes, sandals
- **Accessories**: Fashion accessories, quality bags, sunglasses, cashmere scarf

### Essential Items (Core Products)
Found in most stores for consistency:
- Classic Cotton T-Shirt (APP-TS-001)
- Classic Straight Leg Jeans (APP-JN-001)
- Rain Jacket Waterproof (OUT-JK-006)
- Classic White Sneakers (FW-SN-001)
- Baseball Cap Classic (ACC-CP-001)
- Athletic Crew Socks Pack (ACC-SK-001)

---

## Seasonal Inventory Management

### Washington State Seasonal Patterns

The inventory system uses **monthly multipliers** to reflect Pacific Northwest weather and consumer behavior.

#### Category Multipliers by Month

| Category | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec | Peak Season |
|----------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-------------|
| **Apparel - Tops** | 0.7 | 0.7 | 0.8 | 0.9 | 1.1 | 1.3 | 1.4 | 1.3 | 1.1 | 0.9 | 0.7 | 0.6 | Summer (Jul) |
| **Apparel - Bottoms** | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | Stable |
| **Outerwear** | 1.8 | 1.7 | 1.5 | 1.3 | 1.0 | 0.7 | 0.6 | 0.6 | 0.9 | 1.3 | 1.6 | 1.8 | Winter (Dec-Jan) |
| **Footwear** | 0.9 | 0.9 | 1.0 | 1.1 | 1.2 | 1.3 | 1.4 | 1.3 | 1.2 | 1.1 | 0.9 | 0.8 | Summer (Jul) |
| **Accessories** | 1.2 | 1.2 | 1.1 | 1.0 | 1.0 | 1.1 | 1.2 | 1.2 | 1.1 | 1.0 | 1.1 | 1.3 | Winter (Dec) |

### Seasonal Insights

#### ❄️ Winter (December - February)
- **Outerwear**: 80% increase in demand (rain jackets, parkas, warm coats)
- **Accessories**: 20-30% increase (beanies, gloves, scarves)
- **Footwear**: 10-20% decrease (boots stay stable, sandals minimal)
- **Tops/Bottoms**: 30-40% decrease in light summer clothing

**Inventory Strategy**: High stock of waterproof jackets (essential for wet PNW winters), warm layers, winter accessories

#### 🌸 Spring (March - May)
- **Transition Period**: Gradual shift from winter to summer items
- **Outerwear**: Demand decreases but rain jackets remain important
- **Footwear**: Increasing demand for sneakers and hiking boots
- **Tops**: Rising demand for lighter shirts and tees

**Inventory Strategy**: Balanced mix, maintain rain gear, phase in summer items

#### ☀️ Summer (June - August)
- **Tops**: Peak season (40% increase) - t-shirts, tank tops
- **Footwear**: Peak season (40% increase) - sneakers, sandals
- **Outerwear**: Minimal (40% decrease) - light jackets only
- **Accessories**: Moderate increase - sunglasses, caps, summer hats

**Inventory Strategy**: High stock of casual wear, athletic gear, outdoor activity items

#### 🍂 Fall (September - November)
- **Transition Period**: Return to layering and warmer clothing
- **Outerwear**: Rapidly increasing demand
- **Accessories**: Increasing demand for cold weather items
- **Footwear**: Shift toward boots and closed-toe shoes

**Inventory Strategy**: Gradual increase in jackets and cold weather gear, maintain versatile items

### Inventory Levels by Store Type

#### Popup Stores
- **Base Stock**: 5-40 units per product
- **Average Stock**: 8-15 units per product
- **Store Multiplier**: 0.3-1.3x based on customer distribution weight
- **Seasonal Adjustment**: Applied to base stock
- **Random Variation**: ±20% for realism

#### Online Store
- **Base Stock**: 30-120 units per product
- **Average Stock**: 45 units per product
- **Higher Capacity**: Can stock all 129 products
- **Seasonal Adjustment**: Same multipliers as popup stores
- **Order Fulfillment**: Services customers nationwide

### Stock Level Calculation
```
Final Stock = Base Stock × Store Weight × Seasonal Multiplier × Random(0.8-1.2)
Minimum Stock = 2 units (always maintained)
```

**Example**:
- Product: Rain Jacket (Outerwear)
- Month: December
- Store: Pike Place (weight 30)
- Base Stock: 25 units
- Calculation: 25 × 1.3 × 1.8 × 1.0 = 58.5 → 59 units

---

## Supplier Network

### Overview
- **Total Suppliers**: 20 active vendors
- **Preferred Suppliers**: 16 (80%)
- **Average Rating**: 4.7/5.0
- **Geographic Focus**: Washington State (local suppliers prioritized)

### Supplier Directory

#### Premium Suppliers (Rating ≥ 4.8)

**1. Elite Fashion Distributors** ⭐ 4.9
- **Contact**: Sarah Johnson | sarah.j@elitefashion.com | +1-425-555-0102
- **Location**: Bellevue, WA
- **Categories**: Apparel - Tops
- **Products**: Formal Shirts, T-Shirts
- **Terms**: Net 45 | Min Order: $1,000 | Lead Time: 10 days
- **Status**: Preferred Supplier

**2. Footwear Direct International** ⭐ 4.9
- **Contact**: Lisa Thompson | lisa.t@footweardirect.com | +1-425-555-0106
- **Location**: Redmond, WA
- **Categories**: Footwear
- **Products**: Sneakers, Dress Shoes
- **Terms**: Net 45 | Min Order: $1,500 | Lead Time: 18 days
- **Status**: Preferred Supplier

**3. Sock & Hosiery Wholesale** ⭐ 4.9
- **Contact**: Patricia Davis | patricia@socksupply.com | +1-425-555-0112
- **Location**: Bellevue, WA
- **Categories**: Accessories
- **Products**: Socks
- **Terms**: Net 30 | Min Order: $300 | Lead Time: 5 days
- **Status**: Preferred Supplier ⚡ *Fastest Delivery*

**4. Formal Wear Specialists** ⭐ 4.9
- **Contact**: Susan Moore | susan.moore@formalwear.com | +1-206-555-0117
- **Location**: Seattle, WA
- **Categories**: Apparel - Tops, Footwear
- **Products**: Formal Shirts, Dress Shoes
- **Terms**: Net 60 | Min Order: $2,000 | Lead Time: 21 days
- **Status**: Preferred Supplier

**5. Urban Threads Wholesale** ⭐ 4.8
- **Contact**: Michael Chen | michael.chen@urbanthreads.com | +1-206-555-0101
- **Location**: Seattle, WA (Fashion District)
- **Categories**: Apparel - Tops, Apparel - Bottoms
- **Products**: T-Shirts, Jeans
- **Terms**: Net 30 | Min Order: $500 | Lead Time: 14 days
- **Status**: Preferred Supplier

**6. Northwest Denim Works** ⭐ 4.8
- **Contact**: David Kim | david.kim@nwdenim.com | +1-509-555-0105
- **Location**: Spokane, WA
- **Categories**: Apparel - Bottoms
- **Products**: Jeans (Specialist)
- **Terms**: Net 30 | Min Order: $800 | Lead Time: 15 days
- **Status**: Preferred Supplier

**7. Premier Accessories Ltd** ⭐ 4.8
- **Contact**: Jennifer Lee | j.lee@premieraccessories.com | +1-206-555-0108
- **Location**: Seattle, WA (Market Street)
- **Categories**: Accessories
- **Products**: Caps & Hats, Socks, Backpacks & Bags
- **Terms**: Net 30 | Min Order: $400 | Lead Time: 7 days
- **Status**: Preferred Supplier

**8. Active Wear Solutions** ⭐ 4.8
- **Contact**: Amanda Garcia | amanda@activewear.com | +1-253-555-0110
- **Location**: Tacoma, WA
- **Categories**: Apparel - Tops, Footwear
- **Products**: T-Shirts, Hoodies, Sneakers
- **Terms**: Net 30 | Min Order: $1,000 | Lead Time: 12 days
- **Status**: Preferred Supplier

**9. Fashion Forward Wholesale** ⭐ 4.8
- **Contact**: Michelle Taylor | michelle@fashionforward.com | +1-425-555-0114
- **Location**: Redmond, WA
- **Categories**: Apparel - Tops, Apparel - Bottoms
- **Products**: T-Shirts, Formal Shirts, Jeans
- **Terms**: Net 30 | Min Order: $1,200 | Lead Time: 10 days
- **Status**: Preferred Supplier

**10. Athletic Footwear Network** ⭐ 4.8
- **Contact**: Ryan Clark | ryan.clark@athleticfootwear.com | +1-425-555-0116
- **Location**: Everett, WA
- **Categories**: Footwear
- **Products**: Sneakers (Athletic Specialist)
- **Terms**: Net 30 | Min Order: $900 | Lead Time: 12 days
- **Status**: Preferred Supplier

**11. Quality Basics Wholesale** ⭐ 4.8
- **Contact**: Mark Johnson | mark.j@qualitybasics.com | +1-253-555-0120
- **Location**: Tacoma, WA
- **Categories**: Apparel - Tops, Accessories
- **Products**: T-Shirts, Socks
- **Terms**: Net 30 | Min Order: $500 | Lead Time: 7 days
- **Status**: Preferred Supplier

#### Quality Suppliers (Rating 4.5-4.7)

**12. Pacific Apparel Group** ⭐ 4.7
- **Contact**: James Martinez | james@pacificapparel.com | +1-253-555-0103
- **Location**: Tacoma, WA
- **Categories**: Apparel - Tops, Apparel - Bottoms
- **Products**: Hoodies, Jeans
- **Terms**: Net 30 | Min Order: $750 | Lead Time: 12 days
- **Status**: Preferred Supplier

**13. Comfort Footwear Wholesale** ⭐ 4.7
- **Contact**: Robert Anderson | robert@comfortfootwear.com | +1-425-555-0107
- **Location**: Everett, WA
- **Categories**: Footwear
- **Products**: Sneakers
- **Terms**: Net 30 | Min Order: $600 | Lead Time: 10 days
- **Status**: Preferred Supplier

**14. Bag & Luggage Distributors** ⭐ 4.7
- **Contact**: Daniel White | daniel.white@bagluggage.com | +1-509-555-0113
- **Location**: Spokane, WA
- **Categories**: Accessories
- **Products**: Backpacks & Bags
- **Terms**: Net 45 | Min Order: $800 | Lead Time: 15 days
- **Status**: Preferred Supplier

**15. Streetwear Collective** ⭐ 4.7
- **Contact**: Jason Rodriguez | jason@streetwearcollective.com | +1-425-555-0118
- **Location**: Kirkland, WA
- **Categories**: Apparel - Tops, Accessories
- **Products**: Hoodies, T-Shirts, Caps & Hats
- **Terms**: Net 30 | Min Order: $700 | Lead Time: 10 days
- **Status**: Preferred Supplier

**16. Metro Style Supply Co** ⭐ 4.6
- **Contact**: Emily Rodriguez | e.rodriguez@metrostyle.com | +1-206-555-0104
- **Location**: Seattle, WA
- **Categories**: Outerwear
- **Products**: Jackets
- **Terms**: Net 60 | Min Order: $2,000 | Lead Time: 21 days
- **Status**: Preferred Supplier

**17. Premium Denim Source** ⭐ 4.6
- **Contact**: Kevin Martinez | kevin@premiumdenim.com | +1-253-555-0115
- **Location**: Tacoma, WA
- **Categories**: Apparel - Bottoms
- **Products**: Jeans (Premium)
- **Terms**: Net 45 | Min Order: $1,500 | Lead Time: 20 days
- **Status**: Standard Supplier

**18. Global Headwear Co** ⭐ 4.5
- **Contact**: Chris Wilson | chris.w@globalheadwear.com | +1-425-555-0109
- **Location**: Kirkland, WA
- **Categories**: Accessories
- **Products**: Caps & Hats
- **Terms**: Net 45 | Min Order: $500 | Lead Time: 14 days
- **Status**: Standard Supplier

**19. Winter Wear Supply Co** ⭐ 4.5
- **Contact**: Karen Anderson | karen@winterwear.com | +1-509-555-0119
- **Location**: Spokane, WA
- **Categories**: Outerwear, Accessories
- **Products**: Jackets, Caps & Hats
- **Terms**: Net 45 | Min Order: $1,800 | Lead Time: 25 days
- **Status**: Standard Supplier (Seasonal)

**20. Classic Outerwear Imports** ⭐ 4.4
- **Contact**: Thomas Brown | thomas.brown@classicouterwear.com | +1-206-555-0111
- **Location**: Seattle, WA
- **Categories**: Outerwear
- **Products**: Jackets
- **Terms**: Net 60 | Min Order: $2,500 | Lead Time: 28 days
- **Status**: Standard Supplier

### Supplier Performance Metrics

#### By Category
- **Apparel - Tops**: 8 suppliers (avg rating 4.7)
- **Apparel - Bottoms**: 5 suppliers (avg rating 4.7)
- **Outerwear**: 3 suppliers (avg rating 4.5)
- **Footwear**: 4 suppliers (avg rating 4.8)
- **Accessories**: 7 suppliers (avg rating 4.7)

#### By Lead Time
- **Fast (5-10 days)**: 6 suppliers
- **Standard (11-15 days)**: 9 suppliers
- **Extended (16-21 days)**: 3 suppliers
- **Long (22+ days)**: 2 suppliers

#### By Minimum Order
- **Low ($300-$700)**: 8 suppliers
- **Medium ($750-$1,500)**: 8 suppliers
- **High ($1,800-$2,500)**: 4 suppliers

### Supplier Contracts

All suppliers have active contracts (20 total):
- **Contract Period**: January 2024 - December 2025
- **Contract Values**: $50,000 - $500,000
- **Payment Terms**: Net 30 (60%), Net 45 (25%), Net 60 (15%)
- **Auto-Renewal**: 50% of contracts have auto-renew clauses

---

## Company Policies

### 1. Procurement Policy
**Type**: Procurement  
**Department**: Procurement  
**Approval Required**: Yes  
**Minimum Threshold**: $5,000

**Policy Content**:
> All purchases over $5,000 require manager approval. Competitive bidding required for orders over $25,000.

**Key Requirements**:
- Purchases under $5,000: No approval needed (auto-approved)
- Purchases $5,000 - $25,000: Manager approval required
- Purchases over $25,000: Competitive bidding + executive approval required
- All purchases must be from approved vendors only

**Responsible Approvers**:
- Supervisors: Up to $5,000
- Managers: Up to $50,000
- Directors: Up to $250,000
- Executives: Unlimited

---

### 2. Order Processing Policy
**Type**: Order Processing  
**Department**: Operations  
**Approval Required**: No (Standard Processing)

**Policy Content**:
> Orders processed within 24 hours. Rush orders require $50 fee and manager approval.

**Processing Timeline**:
- **Standard Orders**: 24-hour processing
- **Rush Orders**: Same-day processing (requires approval + $50 fee)
- **Bulk Orders**: 2-3 business days
- **Custom Orders**: 5-7 business days

**Order Prioritization**:
1. Rush orders (approved)
2. Urgent procurement requests
3. Stock replenishment orders
4. Standard customer orders

---

### 3. Budget Authorization
**Type**: Budget Authorization  
**Department**: Finance  
**Approval Required**: Yes

**Policy Content**:
> Spending limits: Manager $50K, Director $250K, Executive $1M+

**Authorization Levels**:

| Role | Approval Limit | Requires Additional Approval |
|------|---------------|----------------------------|
| Supervisor | $5,000 | Manager (over $5K) |
| Manager | $50,000 | Director (over $50K) |
| Director | $250,000 | Executive (over $250K) |
| Executive | $1,000,000+ | Board (over $1M) |

**Budget Tracking**:
- Monthly budget reviews required
- Quarterly variance analysis
- Annual budget planning cycle
- Real-time spending alerts at 80% of limit

---

### 4. Vendor Approval Policy
**Type**: Vendor Approval  
**Department**: Procurement  
**Approval Required**: Yes

**Policy Content**:
> All new vendors require approval and background check completion.

**Vendor Onboarding Process**:
1. **Initial Application**: Vendor submits business information
2. **Background Check**: Credit check, business verification
3. **Procurement Review**: Product quality assessment
4. **Contract Negotiation**: Terms, pricing, lead times
5. **Final Approval**: Executive sign-off required
6. **Vendor Setup**: Added to approved vendor list

**Ongoing Requirements**:
- Annual performance reviews
- Quarterly quality audits
- Contract renewals every 2 years
- Compliance monitoring

**Preferred Vendor Benefits**:
- Priority ordering
- Better payment terms
- Volume discounts
- Dedicated account manager

---

## Procurement & Authorization

### Approval Hierarchy

#### Department Structure

**Finance Department**
- **John Finance Director** (DIR001)
  - Email: john.fin@company.com
  - Approval Limit: $250,000

**Operations Department**
- **Sarah Operations Director** (DIR002)
  - Email: sarah.ops@company.com
  - Approval Limit: $250,000

**Procurement Department**
- **Mike Procurement Manager** (MGR001)
  - Email: mike.proc@company.com
  - Approval Limit: $50,000
- **Amy Procurement Specialist** (SUP002)
  - Email: amy.proc@company.com
  - Approval Limit: $5,000

**Management**
- **Emily Executive VP** (EXEC001)
  - Email: emily.exec@company.com
  - Approval Limit: Unlimited
- **David Manager** (MGR002)
  - Email: david.mgr@company.com
  - Approval Limit: $50,000
- **Lisa Supervisor** (SUP001)
  - Email: lisa.sup@company.com
  - Approval Limit: $5,000

### Procurement Request Workflow

#### Request Lifecycle
1. **Submitted**: Requester creates procurement request
2. **Under Review**: Assigned to appropriate approver based on amount
3. **Approved**: Authorized by approver with sufficient limit
4. **In Progress**: Order placed with supplier
5. **Received**: Goods delivered and inspected
6. **Completed**: Invoice processed and paid

#### Urgency Levels
- **Low**: Standard processing (5-7 business days)
- **Normal**: Priority processing (2-3 business days)
- **High**: Urgent processing (1-2 business days)
- **Critical**: Immediate processing (same day approval required)

#### Sample Procurement Scenarios

**Scenario 1: Small Order**
- **Amount**: $3,500
- **Product**: T-Shirts (200 units)
- **Approver**: Any Supervisor ($5,000 limit)
- **Timeline**: 24-hour approval + 7-day supplier lead time

**Scenario 2: Medium Order**
- **Amount**: $35,000
- **Product**: Winter Jackets (500 units)
- **Approver**: Manager ($50,000 limit)
- **Timeline**: 48-hour approval + 21-day supplier lead time

**Scenario 3: Large Order**
- **Amount**: $150,000
- **Product**: Seasonal inventory replenishment
- **Approver**: Director ($250,000 limit)
- **Timeline**: 3-5 day approval + competitive bidding process

**Scenario 4: Enterprise Order**
- **Amount**: $500,000
- **Product**: Annual supplier contract
- **Approver**: Executive (unlimited)
- **Timeline**: 1-2 week approval + board review

### Current Procurement Metrics

Based on generated sample data (25 active requests):

**By Status**:
- Pending: 40% (10 requests)
- Approved: 50% (12-13 requests)
- Rejected: 10% (2-3 requests)

**By Urgency**:
- Low: 25%
- Normal: 40%
- High: 25%
- Critical: 10%

**By Department**:
- Operations: 30%
- Finance: 25%
- Procurement: 25%
- Management: 20%

**Average Metrics**:
- Order Value: $2,500 - $15,000
- Approval Time: 1-5 days
- Fulfillment Time: 7-30 days depending on supplier

---

## System Integration & Agent Support

### Agent Use Cases

#### 1. Product Availability Queries
**Scenario**: Customer at Pike Place wants product not in stock
- **Agent Action**: Check other store inventories
- **Result**: Find product at Bellevue Square or Online Store
- **Data**: Real-time inventory across all locations

#### 2. Supplier Recommendations
**Scenario**: Store needs to reorder popular items
- **Agent Action**: Analyze supplier performance, lead times, costs
- **Result**: Recommend best supplier for specific product category
- **Data**: Supplier ratings, contracts, performance history

#### 3. Procurement Authorization
**Scenario**: Manager needs approval for $75,000 order
- **Agent Action**: Route to appropriate approver (Director level)
- **Result**: Workflow automation with proper authorization chain
- **Data**: Approval limits, company policies, budget status

#### 4. Seasonal Planning
**Scenario**: Planning winter inventory for Spokane location
- **Agent Action**: Apply seasonal multipliers, recommend stock levels
- **Result**: Optimized inventory based on historical patterns
- **Data**: Seasonal multipliers, sales history, weather patterns

#### 5. Store Product Discovery
**Scenario**: Customer wants specific product category
- **Agent Action**: Match customer needs to store specializations
- **Result**: Direct to most appropriate store location
- **Data**: Store themes, product assignments, customer preferences

### Data Access & APIs

**MCP Servers Available**:
- **Sales Analysis MCP**: Product sales, inventory, orders
- **Finance MCP**: Budget, financial metrics, cost analysis
- **Supplier MCP**: Supplier data, contracts, performance

**Database Access**:
- PostgreSQL with pgvector extension
- Row Level Security (RLS) per store
- Real-time inventory tracking
- Historical sales data (2020-2026)

---

## Appendix

### File References
- **Product Data**: `product_data.json` (129 products)
- **Store Configuration**: `reference_data.json` (8 stores)
- **Store Products**: `store_products.json` (reproducible assignments)
- **Supplier Data**: `supplier_data.json` (20 suppliers)
- **Generator Script**: `generate_zava_postgres.py` (3,000+ lines)

### Database Schema
- **Schema Name**: `retail`
- **Database**: `zava`
- **Tables**: 15+ (stores, products, inventory, orders, suppliers, etc.)
- **Vector Support**: Product embeddings for similarity search

### Contact Information
For system support or data updates, contact:
- **Database Team**: db-admin@zava.com
- **Procurement**: procurement@zava.com
- **Operations**: operations@zava.com

---

**Document Version**: 1.0  
**Generated**: October 10, 2025  
**Next Review**: Quarterly basis
