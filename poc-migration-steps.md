# OutSystems to .NET Migration: POC Steps

## POC Objective
Demonstrate feasibility of AI-assisted migration by converting a representative OutSystems module to a working .NET application.

---

## POC Scope (Recommended)
- 1 OutSystems module
- 5-10 entities
- 3-5 screens
- 5-10 server actions
- 1-2 integrations (if any)

---

## Migration Steps

1. **Export OutSystems Application** - Download OAP file from Service Studio
2. **Extract OML Files** - Unzip OAP to get OML metadata files
3. **Parse OML to JSON** - Run parser script to extract entities, actions, screens
4. **Create .NET Solution** - Set up project structure (API, Domain, Infrastructure)
5. **Generate Entities** - Use AI to convert OutSystems entities to C# classes
6. **Create Database** - Run EF Core migrations, migrate sample data
7. **Generate Services** - Use AI to convert server actions to C# service methods
8. **Generate API Controllers** - Use AI to create REST endpoints
9. **Generate UI Components** - Use AI to convert screens to Blazor/React
10. **Wire Up & Test** - Connect UI to APIs, test end-to-end
11. **Deploy & Demo** - Deploy to environment, demonstrate to client

---

## Detailed Steps

### Step 1: Export OutSystems Application
- Download OAP file from Service Studio (Application → Export)
- Or use LifeTime API to export programmatically

### Step 2: Extract OML Files
- Rename .oap to .zip and extract
- Locate .oml files (XML-based metadata)

### Step 3: Parse OML to JSON
- Run Python parser script on OML files
- Output: JSON with entities, screens, actions, integrations

### Step 4: Create .NET Solution
- Create solution with Clean Architecture structure
- Projects: Domain, Application, Infrastructure, API, Web

### Step 5: Generate Entities (AI)
- Feed entity JSON to AI
- AI generates C# classes with EF Core attributes
- Create DbContext with entity configurations

### Step 6: Create Database
- Run `dotnet ef migrations add` and `dotnet ef database update`
- Import sample data for testing

### Step 7: Generate Services (AI)
- Feed server action logic to AI
- AI generates service interfaces and implementations
- Add logging and error handling

### Step 8: Generate API Controllers (AI)
- Feed service definitions to AI
- AI generates REST controllers with proper routes
- Test with Swagger

### Step 9: Generate UI Components (AI)
- Feed screen structure to AI
- AI generates Blazor/React components
- Apply basic Bootstrap styling

### Step 10: Wire Up & Test
- Connect UI components to API endpoints
- Test all user flows end-to-end
- Fix any issues

### Step 11: Deploy & Demo
- Deploy to local or cloud environment
- Demonstrate side-by-side with OutSystems app
- Present to client

---

## POC Deliverables

| Deliverable | Description |
|-------------|-------------|
| Working .NET Application | Deployed, functional app matching POC scope |
| Source Code | Clean, documented codebase |
| Migration Report | Entities, actions, screens migrated with metrics |
| AI Prompts Used | Documented prompts for reproducibility |
| Effort Estimate | Full migration timeline and cost projection |
| Gap Analysis | Features requiring manual work |

---

## POC Timeline Summary

| Day | Phase | Activities |
|-----|-------|------------|
| 1 | Analysis | Extract, parse, analyze, scope agreement |
| 2 | Data + Logic | Entities, database, start services |
| 3 | Logic + UI | Complete services, APIs, start UI |
| 4 | UI + Integration | Complete UI, integrations |
| 5 | Testing | E2E testing, bug fixes |
| 6 | Demo | Polish, documentation, presentation |

**Total: 4-6 working days**

---

## Step-by-Step Execution Checklist

```
[ ] 1. Obtain OAP/OML files from client
[ ] 2. Extract OML from OAP package
[ ] 3. Run OML parser → JSON metadata
[ ] 4. Review complexity, agree on scope
[ ] 5. AI: Generate entity classes
[ ] 6. Create DbContext, run migrations
[ ] 7. Migrate sample data
[ ] 8. AI: Generate service layer (per action)
[ ] 9. AI: Generate API controllers
[ ] 10. Test APIs via Swagger
[ ] 11. AI: Generate UI components (per screen)
[ ] 12. Wire UI to APIs
[ ] 13. AI: Generate integration services (if any)
[ ] 14. End-to-end testing
[ ] 15. Fix issues, polish
[ ] 16. Deploy demo environment
[ ] 17. Prepare comparison documentation
[ ] 18. Present to client
```

---

## Key Demo Points

1. **Speed** - Show how AI accelerates code generation
2. **Accuracy** - Side-by-side functional comparison
3. **Quality** - Clean, maintainable code output
4. **Flexibility** - Easy to customize generated code
5. **Cost Savings** - Effort comparison vs manual rewrite

---

*Document Version: 1.0*  
*Created: 2026-07-22*
