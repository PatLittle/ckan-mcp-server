---
name: data-exploration
description: Performs exploratory data analysis (EDA) on datasets from CKAN portals and CSV files. Use when analyzing datasets, checking data quality, exploring CSV files, or when the user asks to examine, analyze, or validate data.
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
  - ckan_package_show
  - ckan_organization_show
  - ckan_package_search
  - ckan_datastore_search
  - ckan_find_relevant_datasets
---

# Data Exploration Skill

## Overview

This skill provides comprehensive capabilities for Exploratory Data Analysis (EDA) on datasets from CKAN portals and direct CSV files. It focuses on understanding data structure, assessing quality, identifying patterns, and generating insights.

## Capabilities

### 1. Dataset Discovery & Metadata Analysis
- **CKAN Dataset Exploration**: Search and retrieve datasets from CKAN portals
- **Organization Analysis**: Examine publishers and their datasets
- **Metadata Validation**: Assess completeness and quality of metadata
- **Resource Evaluation**: Analyze available data resources and formats

### 2. Structural Analysis
- **Schema Discovery**: Identify columns, data types, and relationships
- **Data Profiling**: Generate statistical summaries and distributions
- **Format Assessment**: Evaluate data formatting and standards compliance
- **Field Analysis**: Examine individual columns and their characteristics

### 3. Quality Assessment
- **Completeness Checking**: Identify missing values and null patterns
- **Consistency Validation**: Verify internal logical consistency
- **Accuracy Evaluation**: Cross-check totals and calculated fields
- **Temporal Analysis**: Assess time-series completeness and gaps
- **Outlier Detection**: Identify anomalous values and patterns

### 4. Statistical Analysis
- **Descriptive Statistics**: Calculate measures of central tendency and dispersion
- **Distribution Analysis**: Examine value distributions and patterns
- **Correlation Analysis**: Identify relationships between variables
- **Trend Analysis**: Detect temporal patterns and changes
- **Segmentation**: Group and compare data subsets

### 5. Insight Generation
- **Pattern Identification**: Discover meaningful patterns in data
- **Anomaly Detection**: Find unusual values or inconsistencies
- **Quality Scoring**: Assign quality metrics to datasets
- **Recommendation Generation**: Provide actionable improvement suggestions

## Tools & Techniques

### DuckDB Integration
For advanced CSV analysis using SQL:
```bash
# Schema analysis
duckdb -jsonlines -c "DESCRIBE SELECT * FROM read_csv('url')"

# Statistical summarization
duckdb -jsonlines -c "SUMMARIZE SELECT * FROM read_csv('url')"

# Data sampling
duckdb -jsonlines -c "SELECT * FROM read_csv('url') USING SAMPLE N"

# Custom queries
duckdb -jsonlines -c "SELECT column_name, COUNT(*), AVG(value) FROM read_csv('url') GROUP BY column_name"
```

### CKAN MCP Tools
- `ckan_package_show` - Detailed dataset metadata
- `ckan_organization_show` - Publisher information
- `ckan_package_search` - Dataset discovery
- `ckan_datastore_search` - DataStore query capabilities
- `ckan_find_relevant_datasets` - Semantic search

### Analysis Patterns

#### Quality Assessment Workflow
```
1. Metadata Validation
   - Check title, description, license
   - Verify publisher information
   - Assess tag relevance

2. Structural Analysis
   - Examine schema and data types
   - Check column naming conventions
   - Validate data formats

3. Content Analysis
   - Assess completeness (null values)
   - Verify consistency (internal logic)
   - Check accuracy (calculated fields)

4. Statistical Profiling
   - Generate descriptive statistics
   - Analyze distributions
   - Identify outliers

5. Insight Generation
   - Detect patterns and trends
   - Generate quality score
   - Provide recommendations
```

## Usage Examples

### Basic EDA Workflow
```markdown
User: "Analyze this dataset from dati.gov.it"

1. Retrieve dataset metadata using ckan_package_show
2. Download and examine CSV structure
3. Generate statistical summary
4. Check data quality metrics
5. Identify key insights and patterns
6. Produce comprehensive report
```

### Quality Assessment
```markdown
User: "Check the quality of this CSV file"

1. Examine file structure and schema
2. Check for missing values
3. Validate data types and formats
4. Verify internal consistency
5. Generate quality score (0-10)
6. Provide improvement recommendations
```

### Comparative Analysis
```markdown
User: "Compare these two datasets"

1. Retrieve both datasets
2. Analyze schemas and structures
3. Compare statistical profiles
4. Identify similarities and differences
5. Highlight quality differences
6. Generate comparison report
```

## Best Practices

### Data Access
1. **Verify URLs**: Always check that data URLs are accessible
2. **Handle Errors**: Gracefully manage missing data and timeouts
3. **Respect Limits**: Be aware of API rate limits and file sizes
4. **Use Raw URLs**: Prefer direct file URLs over GitHub web interfaces

### Analysis Approach
1. **Start with Metadata**: Understand the dataset before diving into data
2. **Profile First**: Generate statistics before detailed analysis
3. **Validate Early**: Check data quality before drawing conclusions
4. **Document Findings**: Keep clear records of analysis steps

### Quality Assessment
1. **Be Systematic**: Follow a consistent quality checklist
2. **Check Calculations**: Verify that totals and percentages are correct
3. **Look for Patterns**: Identify temporal and categorical patterns
4. **Context Matters**: Consider domain-specific quality criteria

### Output Generation
1. **Clear Structure**: Use headings and sections for readability
2. **Visual Elements**: Include tables and code blocks where helpful
3. **Actionable Insights**: Focus on practical recommendations
4. **Quality Scores**: Provide quantitative assessments when possible

## Output Formats

### Standard Report Structure
```markdown
# Dataset Analysis Report

## Metadata Overview
- Title, Publisher, License
- Creation date, modification date
- Resource count and formats

## Structural Analysis
- Schema table (columns, types)
- Data format assessment
- Naming convention evaluation

## Quality Assessment
- Completeness score (0-10)
- Consistency evaluation
- Accuracy verification
- Overall quality score

## Statistical Profile
- Key statistics table
- Distribution analysis
- Outlier detection
- Trend analysis

## Key Insights
- Important patterns discovered
- Notable anomalies found
- Quality improvement recommendations

## Technical Details
- Analysis methods used
- Tools and queries executed
- Limitations and assumptions
```

### Quality Scoring System
```
| Criterion          | Weight | Description                          |
|--------------------|--------|--------------------------------------|
| Completeness       | 30%    | Percentage of non-null values        |
| Consistency        | 25%    | Internal logical coherence           |
| Accuracy           | 20%    | Correctness of calculations          |
| Metadata Quality   | 15%    | Completeness of documentation        |
| Format Standards   | 10%    | Compliance with best practices       |
```

## Performance Considerations

1. **Large Datasets**: Use sampling (`USING SAMPLE N`) for initial exploration
2. **Complex Queries**: Break into smaller, focused analyses
3. **Memory Usage**: Be mindful of context window limitations
4. **Timeout Handling**: Set appropriate timeouts for external requests

## Error Handling

1. **Missing Data**: Clearly indicate when data is unavailable
2. **Format Issues**: Handle malformed data gracefully
3. **API Errors**: Provide meaningful error messages
4. **Timeouts**: Suggest alternative approaches when operations fail

## Integration with Other Skills

This skill can work alongside:
- `code-analysis`: For examining data processing scripts
- `documentation`: For improving dataset documentation
- `visualization`: For creating data visualizations
- `reporting`: For generating comprehensive reports

## Related Files

- `.claude/commands/openspec/` - OpenSpec command templates
- `AGENTS.md` - Agent guidelines and rules
- `docs/skills/skills.md` - General skills documentation
- `docs/europe/openapi.yaml` - API specifications
