using Trade.Api.Models;

namespace Trade.Api.Services;

/// <summary>
/// Service interface for NewEntry CRUD operations
/// </summary>
public interface INewEntryService
{
    Task<IEnumerable<NewEntry>> GetAllAsync(CancellationToken ct = default);
    Task<NewEntry?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<NewEntry?> GetByIdWithDetailsAsync(int id, CancellationToken ct = default);
    Task<NewEntry> CreateAsync(NewEntry entry, CancellationToken ct = default);
    Task<NewEntry?> UpdateAsync(int id, NewEntry entry, CancellationToken ct = default);
    Task<bool> DeleteAsync(int id, CancellationToken ct = default);
    Task<IEnumerable<NewEntry>> GetByBranchAsync(string branchName, CancellationToken ct = default);
    Task<IEnumerable<NewEntry>> GetFinalizedAsync(CancellationToken ct = default);
}
