# Short Economic Report Update

## Changes in the short report

### **Before update:**
- Report showed only **best region** for each product
- Title: "Best Regions for Production"
- One table per product with the best region

### **After update:**
- Report shows **one example from each product and each quality (Q1-Q5)**
- Title: "Production Examples by Product and Quality"
- One table per product with all qualities Q1-Q5

## Report structure

### **Section 3: Production Examples by Product and Quality**

For each product it shows:
- **Region** - best region for this product
- **Country** - region's country
- **Score** - efficiency score
- **Bonus** - regional bonus
- **Q1-Q5** - production for each quality

### **Table example:**

| Region | Country | Score | Bonus | Q1 | Q2 | Q3 | Q4 | Q5 |
|--------|---------|-------|-------|----|----|----|----|----|
| Sample Region 2 | Sample Country | 64.47 | 20.0% | 213 | 155 | 113 | 83 | 60 |

## Products in the report

1. **Weapon** - land weapon
2. **Grain** - grain (raw material)
3. **Iron** - iron (raw material)
4. **Titanium** - titanium (raw material)
5. **Fuel** - fuel (raw material)
6. **Aircraft** - air weapon
7. **Food** - food
8. **Airplane Ticket** - airplane tickets

## Benefits

- **Complete overview** of all products and qualities
- **Easy comparison** of Q1-Q5 production
- **Best regions** for each product
- **Concise format** - one row per product

## Usage

```bash
python3 main.py short-economic-report
```

The report will be saved in the `reports/` directory as a DOCX file.

