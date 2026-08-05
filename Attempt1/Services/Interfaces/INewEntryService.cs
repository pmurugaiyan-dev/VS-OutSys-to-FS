using DemoApplication.Models.Entities;

namespace DemoApplication.Services.Interfaces;

/// <summary>
/// Service interface for NewEntry operations.
/// Migrated from OutSystems Trade module.
/// </summary>
public interface INewEntryService
{
    Task<NewEntry?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<IEnumerable<NewEntry>> GetAllAsync(CancellationToken ct = default);
    Task<NewEntry> CreateAsync(NewEntry entity, CancellationToken ct = default);
    Task UpdateAsync(NewEntry entity, CancellationToken ct = default);
    Task DeleteAsync(int id, CancellationToken ct = default);
    Task<IEnumerable<NewEntry>> SearchAsync(string? barCode, string? branchName, CancellationToken ct = default);
}
