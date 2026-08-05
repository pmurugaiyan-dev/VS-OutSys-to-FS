using Microsoft.EntityFrameworkCore;
using DemoApplication.Models.Entities;

namespace DemoApplication.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
    {
    }
    
    // Local entity defined in Trade module
    public DbSet<NewEntry> NewEntries { get; set; }
    
    // Note: The following entities are referenced from external OutSystems modules:
    // - User (from Users module)
    // - Sample_Employee, Sample_Department, etc. (from SampleData_CS)
    // - Account, Transaction (from Sample_BankingAccount_CS)
    // - Customer, Employee, JobPosition, Department (from Sample_Customer_CS, Sample_Employee_CS)
    // These would need to be imported from their respective modules or recreated.
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        
        modelBuilder.Entity<NewEntry>(entity =>
        {
            entity.ToTable("NewEntry");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Id).ValueGeneratedOnAdd();
        });
    }
}
