using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using DemoApplication.Models.Entities;
using DemoApplication.Services.Interfaces;

namespace DemoApplication.Pages;

public class IndexModel : PageModel
{
    private readonly INewEntryService _service;

    public IndexModel(INewEntryService service)
    {
        _service = service;
    }

    public IEnumerable<NewEntry> Entries { get; set; } = [];

    [BindProperty]
    public NewEntry NewEntry { get; set; } = new();

    public async Task OnGetAsync()
    {
        Entries = await _service.GetAllAsync();
    }

    public async Task<IActionResult> OnPostAsync()
    {
        try
        {
            if (NewEntry.Time == null || NewEntry.Time == default)
                NewEntry.Time = DateTime.Now;

            await _service.CreateAsync(NewEntry);
        }
        catch (Exception ex)
        {
            ModelState.AddModelError(string.Empty, ex.Message);
            Entries = await _service.GetAllAsync();
            return Page();
        }
        return RedirectToPage();
    }

    public async Task<IActionResult> OnPostDeleteAsync(int id)
    {
        await _service.DeleteAsync(id);
        return RedirectToPage();
    }
}
