using Microsoft.EntityFrameworkCore;
using Trade.Api.Data;
using Trade.Api.Models;

namespace Trade.Api.Services;

/// <summary>
/// Service implementation for NewEntry CRUD operations
/// Migrated from OutSystems server actions
/// </summary>
public class NewEntryService : INewEntryService
{
    private readonly TradeDbContext _context;
    private readonly ILogger<NewEntryService> _logger;

    public NewEntryService(TradeDbContext context, ILogger<NewEntryService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<IEnumerable<NewEntry>> GetAllAsync(CancellationToken ct = default)
    {
        _logger.LogInformation("Retrieving all NewEntry records");
        return await _context.NewEntries
            .OrderByDescending(e => e.Time)
            .ToListAsync(ct);
    }

    public async Task<NewEntry?> GetByIdAsync(int id, CancellationToken ct = default)
    {
        _logger.LogInformation("Retrieving NewEntry with Id: {Id}", id);
        return await _context.NewEntries.FindAsync(new object[] { id }, ct);
    }

    public async Task<NewEntry?> GetByIdWithDetailsAsync(int id, CancellationToken ct = default)
    {
        _logger.LogInformation("Retrieving NewEntry with details, Id: {Id}", id);
        return await _context.NewEntries
            .Include(e => e.DetailItems)
            .FirstOrDefaultAsync(e => e.Id == id, ct);
    }

    public async Task<NewEntry> CreateAsync(NewEntry entry, CancellationToken ct = default)
    {
        _logger.LogInformation("Creating new NewEntry for Branch: {BranchName}", entry.BranchName);
        
        entry.Time = DateTime.UtcNow;
        _context.NewEntries.Add(entry);
        await _context.SaveChangesAsync(ct);
        
        _logger.LogInformation("Created NewEntry with Id: {Id}", entry.Id);
        return entry;
    }

    public async Task<NewEntry?> UpdateAsync(int id, NewEntry entry, CancellationToken ct = default)
    {
        var existing = await _context.NewEntries.FindAsync(new object[] { id }, ct);
        if (existing == null)
        {
            _logger.LogWarning("NewEntry with Id: {Id} not found for update", id);
            return null;
        }

        existing.WeightLbs = entry.WeightLbs;
        existing.BarCode = entry.BarCode;
        existing.BranchName = entry.BranchName;
        existing.Items = entry.Items;
        existing.Final = entry.Final;

        await _context.SaveChangesAsync(ct);
        _logger.LogInformation("Updated NewEntry with Id: {Id}", id);
        
        return existing;
    }

    public async Task<bool> DeleteAsync(int id, CancellationToken ct = default)
    {
        var entry = await _context.NewEntries.FindAsync(new object[] { id }, ct);
        if (entry == null)
        {
            _logger.LogWarning("NewEntry with Id: {Id} not found for deletion", id);
            return false;
        }

        _context.NewEntries.Remove(entry);
        await _context.SaveChangesAsync(ct);
        _logger.LogInformation("Deleted NewEntry with Id: {Id}", id);
        
        return true;
    }

    public async Task<IEnumerable<NewEntry>> GetByBranchAsync(string branchName, CancellationToken ct = default)
    {
        _logger.LogInformation("Retrieving NewEntry records for Branch: {BranchName}", branchName);
        return await _context.NewEntries
            .Where(e => e.BranchName == branchName)
            .OrderByDescending(e => e.Time)
            .ToListAsync(ct);
    }

    public async Task<IEnumerable<NewEntry>> GetFinalizedAsync(CancellationToken ct = default)
    {
        _logger.LogInformation("Retrieving finalized NewEntry records");
        return await _context.NewEntries
            .Where(e => e.Final)
            .OrderByDescending(e => e.Time)
            .ToListAsync(ct);
    }
}
