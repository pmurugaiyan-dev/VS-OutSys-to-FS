# OutSystems to .NET Migration Demo Script

## Pre-Demo Setup
- Source files location: `C:\Users\Mohan\Documents\AI Apps\BP OutSystems`
  - DemoApplication.oap (extracted OAP)
  - Trade.oml (binary OML)
  - Trade.xml (converted XML - ready for parsing)
- Target folder: `C:\Repositories\VS OutSys to FS\Attempt 2 Demo`

## Demo Prompt

Copy and paste this prompt to start the migration:

---

**Prompt:**

```
Migrate the OutSystems Trade module to .NET 8 Web API.

Source files are in: C:\Users\Mohan\Documents\AI Apps\BP OutSystems
- Trade.xml contains the converted OML with entity definitions

Generate the .NET application in: C:\Repositories\VS OutSys to FS\Attempt 2 Demo

Use the agents in the agents folder:
1. Parser Agent - to parse Trade.xml and extract entities
2. Analyzer Agent - to analyze complexity
3. Configuration Agent - to generate project files
4. Compilation Agent - to build and verify

The Trade module has:
- NewEntry entity with fields: Weight_Lbs, BarCode, BranchName, Items, Time, Final
- MasterDetailItem structure

Generate complete .NET 8 Web API with:
- Entity models
- DbContext
- Services with CRUD operations
- API Controllers
- Razor Pages UI at /Trade route
- Swagger documentation

Use InMemory database for demo purposes.
```

---

## Expected Demo Flow

1. **Parser Agent** - Parses Trade.xml, extracts NewEntry entity (7 attributes)
2. **Analyzer Agent** - Reports complexity score (5.5 - Low)
3. **Configuration Agent** - Generates project files (csproj, Program.cs, appsettings)
4. **Code Generation** - Creates Models, Services, Controllers, Pages
5. **Compilation Agent** - Runs `dotnet build` - BUILD SUCCEEDED

## Post-Demo

After recording, manually run:
```powershell
cd "C:\Repositories\VS OutSys to FS\Attempt 2 Demo"
dotnet run
```

Access: http://localhost:5000/Trade
