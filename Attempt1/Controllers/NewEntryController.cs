using Microsoft.AspNetCore.Mvc;
using DemoApplication.Models.Entities;
using DemoApplication.Services.Interfaces;

namespace DemoApplication.Controllers;

/// <summary>
/// API Controller for NewEntry entity.
/// Migrated from OutSystems Trade module.
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class NewEntryController : ControllerBase
{
    private readonly INewEntryService _service;
    private readonly ILogger<NewEntryController> _logger;

    public NewEntryController(INewEntryService service, ILogger<NewEntryController> logger)
    {
        _service = service;
        _logger = logger;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<NewEntry>>> GetAll(CancellationToken ct)
    {
        _logger.LogInformation("Getting all NewEntry records");
        var entries = await _service.GetAllAsync(ct);
        return Ok(entries);
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<NewEntry>> GetById(int id, CancellationToken ct)
    {
        _logger.LogInformation("Getting NewEntry with Id {Id}", id);
        var entry = await _service.GetByIdAsync(id, ct);
        
        if (entry == null)
        {
            return NotFound();
        }
        
        return Ok(entry);
    }

    [HttpPost]
    public async Task<ActionResult<NewEntry>> Create([FromBody] NewEntry entry, CancellationToken ct)
    {
        _logger.LogInformation("Creating new NewEntry");
        var created = await _service.CreateAsync(entry, ct);
        return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
    }

    [HttpPut("{id}")]
    public async Task<IActionResult> Update(int id, [FromBody] NewEntry entry, CancellationToken ct)
    {
        if (id != entry.Id)
        {
            return BadRequest("Id mismatch");
        }

        _logger.LogInformation("Updating NewEntry with Id {Id}", id);
        await _service.UpdateAsync(entry, ct);
        return NoContent();
    }

    [HttpDelete("{id}")]
    public async Task<IActionResult> Delete(int id, CancellationToken ct)
    {
        _logger.LogInformation("Deleting NewEntry with Id {Id}", id);
        await _service.DeleteAsync(id, ct);
        return NoContent();
    }

    [HttpGet("search")]
    public async Task<ActionResult<IEnumerable<NewEntry>>> Search(
        [FromQuery] string? barCode,
        [FromQuery] string? branchName,
        CancellationToken ct)
    {
        _logger.LogInformation("Searching NewEntry with BarCode={BarCode}, BranchName={BranchName}", barCode, branchName);
        var results = await _service.SearchAsync(barCode, branchName, ct);
        return Ok(results);
    }
}
