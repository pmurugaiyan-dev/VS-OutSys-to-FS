using Microsoft.EntityFrameworkCore;
using Trade.Api.Models;

namespace Trade.Api.Data;

/// <summary>
/// Database context for Trade module - Migrated from OutSystems
/// </summary>
public class TradeDbContext : DbContext
{
    public TradeDbContext(DbContextOptions<TradeDbContext> options) : base(options)
    {
    }

    public DbSet<NewEntry> NewEntries { get; set; } = null!;
    public DbSet<MasterDetailItem> MasterDetailItems { get; set; } = null!;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // NewEntry configuration
        modelBuilder.Entity<NewEntry>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.BarCode);
            
            // Master-Detail relationship
            entity.HasMany(e => e.DetailItems)
                  .WithOne(d => d.NewEntry)
                  .HasForeignKey(d => d.NewEntryId)
                  .OnDelete(DeleteBehavior.Cascade);
        });

        // MasterDetailItem configuration
        modelBuilder.Entity<MasterDetailItem>(entity =>
        {
            entity.HasKey(e => e.Id);
        });
    }
}
