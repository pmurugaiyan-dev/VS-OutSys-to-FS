using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace DemoApplication.Models.Entities;

/// <summary>
/// Entity migrated from OutSystems: NewEntry
/// Pretty Name: New Entry
/// Created By: sivapurapu.srikanth@wipro.com
/// Last Modified: 2026-07-24 06:51:30
/// </summary>
[Table("NewEntry")]
public class NewEntry
{
    [Key]
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; set; }
    
    [MaxLength(500)]
    public string? Weight_Lbs { get; set; }
    
    [MaxLength(100)]
    public string? BarCode { get; set; }
    
    [MaxLength(200)]
    public string? BranchName { get; set; }
    
    [MaxLength(1000)]
    public string? Items { get; set; }
    
    public DateTime? Time { get; set; }
    
    [MaxLength(500)]
    public string? Final { get; set; }
}
