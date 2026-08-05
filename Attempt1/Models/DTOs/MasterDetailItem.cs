namespace DemoApplication.Models.DTOs;

/// <summary>
/// Structure migrated from OutSystems: MasterDetailItem
/// Used for master-detail UI patterns.
/// </summary>
public class MasterDetailItem
{
    public int Id { get; set; }
    
    public string Title { get; set; } = string.Empty;
    
    public string Description { get; set; } = string.Empty;
    
    public string ImageUrl { get; set; } = string.Empty;
}
