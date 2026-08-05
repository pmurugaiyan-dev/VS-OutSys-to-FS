using Microsoft.AspNetCore.Mvc;
using Trade.Api.Models;
using Trade.Api.Services;

namespace Trade.Api.Controllers;

/// <summary>
/// API Controller for NewEntry operations
/// Migrated from OutSystems Trade module
/// </summary>
[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class NewEntryController : ControllerBase
{
    private readonly INewEntryService _service;
    private readonly ILogger<NewEntryController> _logger;

    public NewEntryController(INewEntryService service, ILogger<NewEntryController> logger)
    {
        _service = service;
        _logger = logger;
    }

    /// <summary>
    /// Get all NewEntry records
    /// </summary>
    /// <returns>List of NewEntry records</returns>
    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<NewEntry>), StatusCodes.Status200OK)]
    public async Task<ActionResult<IEnumerable<NewEntry>>> GetAll(CancellationToken ct)
    {
        var entries = await _service.GetAllAsync(ct);
        return Ok(entries);
    }

    /// <summary>
    /// Get a specific NewEntry by ID
    /// </summary>
    /// <param name="id">NewEntry ID</param>
    /// <param name="ct">Cancellation token</param>
    /// <returns>NewEntry record</returns>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(NewEntry), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<NewEntry>> GetById(int id, CancellationToken ct)
    {
        var entry = await _service.GetByIdAsync(id, ct);
        if (entry == null)
        {
            return NotFound(new { message = $"NewEntry with ID {id} not found" });
        }
        return Ok(entry);
    }

    /// <summary>
    /// Get a specific NewEntry with detail items
    /// </summary>
    /// <param name="id">NewEntry ID</param>
    /// <param name="ct">Cancellation token</param>
    /// <returns>NewEntry with MasterDetailItems</returns>
    [HttpGet("{id}/details")]
    [ProducesResponseType(typeof(NewEntry), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<NewEntry>> GetWithDetails(int id, CancellationToken ct)
    {
        var entry = await _service.GetByIdWithDetailsAsync(id, ct);
        if (entry == null)
        {
            return NotFound(new { message = $"NewEntry with ID {id} not found" });
        }
        return Ok(entry);
    }

    /// <summary>
    /// Create a new NewEntry
    /// </summary>
    /// <param name="entry">NewEntry data</param>
    /// <param name="ct">Cancellation token</param>
    /// <returns>Created NewEntry</returns>
    [HttpPost]
    [ProducesResponseType(typeof(NewEntry), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<NewEntry>> Create([FromBody] NewEntry entry, CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        var created = await _service.CreateAsync(entry, ct);
        return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
    }

    /// <summary>
    /// Update an existing NewEntry
    /// </summary>
    /// <param name="id">NewEntry ID</param>
    /// <param name="entry">Updated NewEntry data</param>
    /// <param name="ct">Cancellation token</param>
    /// <returns>Updated NewEntry</returns>
    [HttpPut("{id}")]
    [ProducesResponseType(typeof(NewEntry), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<NewEntry>> Update(int id, [FromBody] NewEntry entry, CancellationToken ct)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        var updated = await _service.UpdateAsync(id, entry, ct);
        if (updated == null)
        {
            return NotFound(new { message = $"NewEntry with ID {id} not found" });
        }
        return Ok(updated);
    }

    /// <summary>
    /// Delete a NewEntry
    /// </summary>
    /// <param name="id">NewEntry ID</param>
    /// <param name="ct">Cancellation token</param>
    /// <returns>No content if successful</returns>
    [HttpDelete("{id}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Delete(int id, CancellationToken ct)
    {
        var result = await _service.DeleteAsync(id, ct);
        if (!result)
        {
            return NotFound(new { message = $"NewEntry with ID {id} not found" });
        }
        return NoContent();
    }

    /// <summary>
    /// Get NewEntry records by branch name
    /// </summary>
    /// <param name="branchName">Branch name filter</param>
    /// <param name="ct">Cancellation token</param>
    /// <returns>List of NewEntry records for the branch</returns>
    [HttpGet("branch/{branchName}")]
    [ProducesResponseType(typeof(IEnumerable<NewEntry>), StatusCodes.Status200OK)]
    public async Task<ActionResult<IEnumerable<NewEntry>>> GetByBranch(string branchName, CancellationToken ct)
    {
        var entries = await _service.GetByBranchAsync(branchName, ct);
        return Ok(entries);
    }

    /// <summary>
    /// Get all finalized NewEntry records
    /// </summary>
    /// <param name="ct">Cancellation token</param>
    /// <returns>List of finalized NewEntry records</returns>
    [HttpGet("finalized")]
    [ProducesResponseType(typeof(IEnumerable<NewEntry>), StatusCodes.Status200OK)]
    public async Task<ActionResult<IEnumerable<NewEntry>>> GetFinalized(CancellationToken ct)
    {
        var entries = await _service.GetFinalizedAsync(ct);
        return Ok(entries);
    }
}
