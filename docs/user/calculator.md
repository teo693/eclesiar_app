# 🏭 Eclesiar Regional Productivity Calculator

## 📋 Description

The Regional Productivity Calculator is a tool for calculating optimal production in different regions of the Eclesiar game. It takes into account all 8 factors affecting production according to the official game documentation.

## 🚀 Available Tools

### 1. **Interactive Calculator** (`production_calculator.py`)
Full-featured calculator with interactive user interface.

**Launch:**
```bash
python3 production_calculator.py
```

**Features:**
- ✅ **Flexible region selection**:
  - Select from numbered list
  - **Type region name directly (case insensitive)**
  - **Search by partial region or country name**
  - Smart matching with multiple results handling
- ✅ Product selection (grain, iron, weapon, aircraft, etc.)
- ✅ Company parameter configuration:
  - Company tier (Q1-Q5)
  - Eco Skill (0-100)
  - Number of workers (0-100)
  - Company owner (NPC/Player)
  - Military Base level (0-5)
  - Production building levels (0-5)
  - Company status (for sale/active)
- ✅ Detailed results with efficiency analysis
- ✅ Optimization recommendations

### 2. **Quick Calculator** (`quick_calculator.py`)
Simplified version for quick testing of different scenarios.

**Launch:**
```bash
python3 quick_calculator.py
```

**Features:**
- ✅ **Two modes available**:
  - **Test scenarios mode**: Automatic testing of different scenarios
  - **Interactive mode**: Manual region and parameter selection
- ✅ **Interactive region selection**:
  - Type region name directly (case insensitive)
  - Search by partial region or country name
  - Smart matching with multiple results handling
- ✅ Comparison of results for different parameters
- ✅ Quick verification of different factor impacts

## 📊 Production Factors

The calculator takes into account all 8 factors from the Eclesiar documentation:

### 1. **NPC Company Owner**
- Production divided by 3 for products (Industrial Zone)
- Raw materials (Production Field) remain unchanged

### 2. **Military Base Bonus**
- 5% bonus for weapons and air-weapons with level 3+ military base

### 3. **Consecutive Workers Debuff**
- `production = production * (1.3 - (workers_today / 10))`
- Minimum 10% production

### 4. **Eco Skill Bonus**
- `production = int(production * (1 + eco_skill / 50))`
- Rounded down

### 5. **Region and Country Bonus**
- **Regional Bonus**: Region-specific production bonus from API (bonus_score)
- **Country Bonus**: Dynamic calculation based on regional bonuses within a country
  - Formula: `sum of regional bonuses of same type in country / 5`
  - Automatically calculated for each production type
  - Deduplication logic prevents counting duplicate regions

### 6. **Pollution Debuff**
- `production = production - ((production - (production*0.1)) * pollution_value)`
- According to documentation formula

### 7. **Production Fields/Industrial Zones**
- 5% bonus per building level
- Production Fields for raw materials, Industrial Zones for products

### 8. **Company State**
- Production divided by 2 if company is for sale

## 📈 Results Interpretation

### **Efficiency Score**
- **> 100**: 🟢 Very good efficiency
- **80-100**: 🟡 Good efficiency  
- **60-80**: 🟠 Average efficiency
- **< 60**: 🔴 Low efficiency

### **Production by Quality**
- **Q1-Q5**: Production for each quality level
- **Proportions**: Maintained according to base values

### **Region Statistics**
- **Regional Bonus**: Production bonus of the region
- **Country Bonus**: Dynamic country bonus calculation
- **Pollution**: Impact on production
- **NPC Wages**: Operating costs in GOLD

## 🎯 Usage Examples

### **Region Selection Examples**

#### **Method 1: Number Selection**
```
Select region: 5
✅ Selected: Warsaw (Poland)
```

#### **Method 2: Direct Name Input**
```
Select region: warsaw
✅ Found: Warsaw (Poland)
```

#### **Method 3: Partial Name Search**
```
Select region: war
🔍 Found 3 matching regions:
   1. Warsaw (Poland)
   2. Warwick (United Kingdom)  
   3. Warmia (Poland)
Select specific region (1-3): 1
✅ Selected: Warsaw (Poland)
```

#### **Method 4: Country Name Search**
```
Select region: poland
🔍 Found 5 matching regions:
   1. Warsaw (Poland)
   2. Krakow (Poland)
   3. Gdansk (Poland)
   ...
Select specific region (1-5): 2
✅ Selected: Krakow (Poland)
```

### **Scenario 1: New Player**
```python
# Q1 company, eco skill 0, no workers
company_tier = 1
eco_skill = 0
workers_today = 0
```

### **Scenario 2: Experienced Player**
```python
# Q5 company, eco skill 50, with workers
company_tier = 5
eco_skill = 50
workers_today = 10
```

### **Scenario 3: Optimal Configuration**
```python
# Q5 company, eco skill 100, full crew, buildings level 5
company_tier = 5
eco_skill = 100
workers_today = 20
building_level = 5
```

## 🔧 Configuration

### **Base Production Values**
Values are defined in `production_analyzer_consolidated.py`:

```python
"weapon": {
    "q1": 197, "q2": 143, "q3": 105, "q4": 77, "q5": 56,
    "building_type": "Industrial Zone"
}
```

### **Bonus Mapping**
```python
"weapon": ["WEAPONS", "weapon", "iron", "general"]
```

## 📝 Sample Results

```
📍 Hurghada (Slovenia) - Weapon
🏢 Q5 | 🎯 Eco: 16 | 👥 Workers: 0
🏭 Building: 0 | 🏛️ Military: 0
👤 Owner: Player | 💰 Sale: No
--------------------------------------------------
Q1:  337 | Q2:  245 | Q3:  180 | Q4:  132 | Q5:   96
🎯 Score: 105.56 | 📈 Regional Bonus: 0.0% | 🌍 Country Bonus: 0.0% | 🌫️ Pollution: 0.0%
```

## 🚨 Troubleshooting

### **Results too low?**
1. Check base production values
2. Increase Eco Skill
3. Hire workers
4. Raise building levels
5. Check region pollution

### **API connection error?**
- Check internet connection
- Ensure Eclesiar API is available
- Check error logs

### **Missing region data?**
- Use sample data
- Check API configuration
- Update region data

## 🔄 Updates

The calculator automatically:
- ✅ Fetches current data from Eclesiar API
- ✅ Includes real NPC wages
- ✅ Updates currency rates
- ✅ Synchronizes region data

## 📞 Support

In case of problems:
1. Check error logs
2. Verify configuration
3. Check Eclesiar API documentation
4. Contact developer

---

**Version**: 2.0  
**Date**: 2025-09-10  
**Compatibility**: Eclesiar API v1.0+
**Features**: Country bonus system, English translation, enhanced tables
