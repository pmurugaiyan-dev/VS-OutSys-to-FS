using System.ComponentModel.DataAnnotations;

namespace Trade.Api.Models;

/// <summary>
/// NewEntry entity - Migrated from OutSystems Trade module
/// Fields: Weight_Lbs, BarCode, BranchName, Items, Time, Final
/// </summary>
public class NewEntry
{
    [Key]
    public int Id { get; set; }

    /// <summary>
    /// Weight in pounds
    /// </summary>
    [Required]
    [Display(Name = "Weight (Lbs)")]
    public decimal WeightLbs { get; set; }

    /// <summary>
    /// Barcode identifier
    /// </summary>
    [Required]
    [MaxLength(100)]
    [Display(Name = "Bar Code")]
    public string BarCode { get; set; } = string.Empty;

    /// <summary>
    /// Branch name
    /// </summary>
    [Required]
    [MaxLength(200)]
    [Display(Name = "Branch Name")]
    public string BranchName { get; set; } = string.Empty;

    /// <summary>
    /// Number of items
    /// </summary>
    [Required]
    [Range(0, int.MaxValue)]
    public int Items { get; set; }

    /// <summary>
    /// Time of entry
    /// </summary>
    [Required]
    public DateTime Time { get; set; }

    /// <summary>
    /// Whether the entry is finalized
    /// </summary>
    public bool Final { get; set; }

    /// <summary>
    /// Collection of detail items (Master-Detail relationship)
    /// </summary>
    public ICollection<MasterDetailItem> DetailItems { get; set; } = new List<MasterDetailItem>();
}
