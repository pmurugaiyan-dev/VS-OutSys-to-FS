using Microsoft.EntityFrameworkCore;
using Trade.Api.Data;
using Trade.Api.Services;

var builder = WebApplication.CreateBuilder(args);

// Database - InMemory for demo
builder.Services.AddDbContext<TradeDbContext>(options =>
    options.UseInMemoryDatabase("TradeDb"));

// Services
builder.Services.AddScoped<INewEntryService, NewEntryService>();

// Controllers
builder.Services.AddControllers();

// Razor Pages for UI
builder.Services.AddRazorPages();

// Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new() { Title = "Trade API", Version = "v1", Description = "Migrated from OutSystems Trade module" });
});

var app = builder.Build();

// Swagger UI
app.UseSwagger();
app.UseSwaggerUI(c =>
{
    c.SwaggerEndpoint("/swagger/v1/swagger.json", "Trade API v1");
});

app.UseStaticFiles();
app.UseRouting();
app.UseAuthorization();

app.MapControllers();
app.MapRazorPages();

// Seed demo data
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<TradeDbContext>();
    db.Database.EnsureCreated();
    
    if (!db.NewEntries.Any())
    {
        db.NewEntries.AddRange(
            new Trade.Api.Models.NewEntry { WeightLbs = 150.5m, BarCode = "BC001", BranchName = "Main Branch", Items = 10, Time = DateTime.Now.AddHours(-2), Final = true },
            new Trade.Api.Models.NewEntry { WeightLbs = 75.25m, BarCode = "BC002", BranchName = "North Branch", Items = 5, Time = DateTime.Now.AddHours(-1), Final = false },
            new Trade.Api.Models.NewEntry { WeightLbs = 200.0m, BarCode = "BC003", BranchName = "South Branch", Items = 15, Time = DateTime.Now, Final = true }
        );
        db.SaveChanges();
    }
}

app.Run();
