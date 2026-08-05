using Microsoft.EntityFrameworkCore;
using DemoApplication.Data;
using DemoApplication.Models.Entities;
using DemoApplication.Services.Interfaces;

namespace DemoApplication.Services;

/// <summary>
/// Service implementation for NewEntry operations.
/// Migrated from OutSystems Trade module.
/// </summary>
public class NewEntryService : INewEntryService
{
    private readonly AppDbContext _context;
    private readonly ILogger<NewEntryService> _logger;

    public NewEntryService(AppDbContext context, ILogger<NewEntryService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<NewEntry?> GetByIdAsync(int id, CancellationToken ct = default)
    {
        return await _context.NewEntries.FindAsync(new object[] { id }, ct);
    }

    public async Task<IEnumerable<NewEntry>> GetAllAsync(CancellationToken ct = default)
    {
        return await _context.NewEntries
            .OrderBy(e => e.Id)
            .ToListAsync(ct);
    }

    public async Task<NewEntry> CreateAsync(NewEntry entity, CancellationToken ct = default)
    {
        _context.NewEntries.Add(entity);
        await _context.SaveChangesAsync(ct);
        _logger.LogInformation("Created NewEntry with Id {Id}", entity.Id);
        return entity;
    }

    public async Task UpdateAsync(NewEntry entity, CancellationToken ct = default)
    {
        _context.Entry(entity).State = EntityState.Modified;
        await _context.SaveChangesAsync(ct);
        _logger.LogInformation("Updated NewEntry with Id {Id}", entity.Id);
    }

    public async Task DeleteAsync(int id, CancellationToken ct = default)
    {
        var entity = await GetByIdAsync(id, ct);
        if (entity != null)
        {
            _context.NewEntries.Remove(entity);
            await _context.SaveChangesAsync(ct);
            _logger.LogInformation("Deleted NewEntry with Id {Id}", id);
        }
    }

    public async Task<IEnumerable<NewEntry>> SearchAsync(string? barCode, string? branchName, CancellationToken ct = default)
    {
        var query = _context.NewEntries.AsQueryable();

        if (!string.IsNullOrWhiteSpace(barCode))
        {
            query = query.Where(e => e.BarCode != null && e.BarCode.Contains(barCode));
        }

        if (!string.IsNullOrWhiteSpace(branchName))
        {
            query = query.Where(e => e.BranchName != null && e.BranchName.Contains(branchName));
        }

        return await query.OrderByDescending(e => e.Id).ToListAsync(ct);
    }
}
