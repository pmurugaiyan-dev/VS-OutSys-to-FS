# Getting Sample OutSystems Files for Testing

## File Formats

| Format | Description | How to Get |
|--------|-------------|------------|
| **OAP** | OutSystems Application Pack | ZIP archive containing OML files. Rename `.oap` to `.zip` and extract. |
| **OML** | OutSystems Module | Binary format requiring Service Studio DLLs to decode to XML. |

## Option 1: OutSystems Forge (Free Account Required)

**URL:** https://www.outsystems.com/forge/list

The Forge is a repository of free, reusable components. To download:

1. Create a free OutSystems account
2. Browse and select a component
3. Install to your environment
4. Export as OAP from Service Studio:
   - Environment > Environment Management > Download Application

**Popular Sample Apps on Forge:**
- Sample App (ID: 4961)
- OutSystems Sample Data (ID: 4145)
- Various training components

## Option 2: OutSystems Training Materials

Training courses include sample OAP files:
- https://www.outsystems.com/training/
- Look for "Lesson Materials" which often include `.oap` files

## Option 3: Export from Free Personal Environment

1. Sign up for free Personal Environment: https://www.outsystems.com/Portal/
2. Create a simple app in Service Studio
3. Save module as OML: File > Save As
4. Export application as OAP: Environment > Download Application

## Option 4: OML to XML Conversion

**Tool:** https://github.com/kelter-antunes/oml-utilities

This C# utility can convert OML files to XML format:
```bash
oml Manipulate "MyModule.oml" "MyModule.xml" O11 --format xml
```

**Note:** Requires OutSystems Service Studio DLLs to be installed.

## OML File Structure (When Decoded to XML)

Based on documentation, OML files contain these XML fragments:

```xml
<Module Name="MyApp" Type="Reactive">
  <!-- Data Layer -->
  <Entity Name="Customer" IsPublic="true">
    <Attribute Name="Id" Type="Integer" IsAutoNumber="true"/>
    <Attribute Name="Name" Type="Text" Length="100" IsMandatory="true"/>
    <Attribute Name="Email" Type="Email"/>
  </Entity>
  
  <StaticEntity Name="OrderStatus">
    <Record><Attribute Name="Label" Value="Pending"/></Record>
    <Record><Attribute Name="Label" Value="Shipped"/></Record>
  </StaticEntity>
  
  <!-- Business Logic -->
  <Action Name="GetCustomerOrders" IsServerAction="true">
    <InputParameter Name="CustomerId" Type="Integer" IsMandatory="true"/>
    <OutputParameter Name="Orders" Type="Order List"/>
    <Aggregate Name="GetOrders">
      <Source Entity="Order"/>
      <Filter Condition="Order.CustomerId = CustomerId"/>
    </Aggregate>
  </Action>
  
  <!-- UI Layer -->
  <Screen Name="CustomerList" Title="Customers">
    <Table Source="Customers">
      <Column Header="Name" Value="Customer.Name"/>
      <Column Header="Email" Value="Customer.Email"/>
    </Table>
  </Screen>
  
  <!-- Integrations -->
  <RESTConsume Name="PaymentAPI" BaseURL="https://api.payment.com">
    <Method Name="ProcessPayment" HTTPMethod="POST" URLPath="/payments"/>
  </RESTConsume>
  
  <!-- Background Jobs -->
  <Timer Name="DailyCleanup" Schedule="Daily at 02:00">
    <Action Name="CleanupOldRecords"/>
  </Timer>
</Module>
```

## Creating a Test Mock File

For testing the parser without real OutSystems files, create an XML file matching the expected structure. See `agents/test_data/` for mock files (to be created).

## Resources

- OML Utilities: https://github.com/kelter-antunes/oml-utilities
- OutSystems Forge: https://www.outsystems.com/forge/list
- OutSystems Forums: https://www.outsystems.com/forums/
- Free Personal Environment: https://www.outsystems.com/Portal/

## Next Steps

Once you have a sample OAP/OML file:

1. If OAP: Rename to `.zip` and extract to get OML files
2. Use OML Utilities to convert OML to XML (requires Service Studio)
3. Or test parser with mock XML files matching expected structure
4. Run: `python agents/main.py <source> -o ./output -n MyApp`
