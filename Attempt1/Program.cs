using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.InMemory;
using Serilog;
using DemoApplication.Data;
using DemoApplication.Services;
using DemoApplication.Services.Interfaces;

var builder = WebApplication.CreateBuilder(args);

// Serilog
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration)
    .Enrich.FromLogContext()
    .WriteTo.Console()
    .CreateLogger();

builder.Host.UseSerilog();

// Database - In-Memory for development (switch to SQL Server for production)
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseInMemoryDatabase("TradeDb"));

// Services - Trade Module
builder.Services.AddScoped<INewEntryService, NewEntryService>();

// Controllers + Razor Pages
builder.Services.AddControllers();
builder.Services.AddRazorPages();

// Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new() { Title = "DemoApplication API - Trade Module", Version = "v1" });
});

// Health checks
builder.Services.AddHealthChecks();

var app = builder.Build();

// Middleware pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();
app.MapRazorPages();
app.MapHealthChecks("/health");

// Redirect root to Trade page
app.MapGet("/", () => Results.Redirect("/Trade"));

// Apply migrations (development only)
if (app.Environment.IsDevelopment())
{
    using var scope = app.Services.CreateScope();
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();
}

app.Run();
