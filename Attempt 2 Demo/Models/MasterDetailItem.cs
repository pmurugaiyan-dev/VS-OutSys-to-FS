using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Trade.Api.Models;

/// <summary>
/// MasterDetailItem structure - Migrated from OutSystems Trade module
/// Represents detail items associated with a NewEntry
/// </summary>
public class MasterDetailItem
{
    [Key]
    public int Id { get; set; }

    /// <summary>
    /// Foreign key to parent NewEntry
    /// </summary>
    [Required]
    public int NewEntryId { get; set; }

    /// <summary>
    /// Navigation property to parent NewEntry
    /// </summary>
    [ForeignKey(nameof(NewEntryId))]
    public NewEntry? NewEntry { get; set; }

    /// <summary>
    /// Item name or description
    /// </summary>
    [Required]
    [MaxLength(200)]
    public string ItemName { get; set; } = string.Empty;

    /// <summary>
    /// Item quantity
    /// </summary>
    [Required]
    [Range(1, int.MaxValue)]
    public int Quantity { get; set; }

    /// <summary>
    /// Unit price
    /// </summary>
    [Required]
    [Column(TypeName = "decimal(18,2)")]
    public decimal UnitPrice { get; set; }

    /// <summary>
    /// Calculated total (Quantity * UnitPrice)
    /// </summary>
    [NotMapped]
    public decimal Total => Quantity * UnitPrice;
}
