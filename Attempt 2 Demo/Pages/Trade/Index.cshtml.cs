using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Trade.Api.Models;
using Trade.Api.Services;

namespace Trade.Api.Pages.Trade;

public class IndexModel : PageModel
{
    private readonly INewEntryService _service;
    private readonly ILogger<IndexModel> _logger;

    public IndexModel(INewEntryService service, ILogger<IndexModel> logger)
    {
        _service = service;
        _logger = logger;
    }

    public IEnumerable<NewEntry>? Entries { get; set; }

    public async Task OnGetAsync()
    {
        Entries = await _service.GetAllAsync();
    }

    public async Task<IActionResult> OnPostCreateAsync(string barCode, string branchName, decimal weightLbs, int items, bool final = false)
    {
        var entry = new NewEntry
        {
            BarCode = barCode,
            BranchName = branchName,
            WeightLbs = weightLbs,
            Items = items,
            Final = final,
            Time = DateTime.UtcNow
        };

        await _service.CreateAsync(entry);
        return RedirectToPage();
    }

    public async Task<IActionResult> OnPostDeleteAsync(int id)
    {
        await _service.DeleteAsync(id);
        return RedirectToPage();
    }
}
