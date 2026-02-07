// Clean Company Name v2
// For use in Clay formulas - replace {{Org}} with your column reference

(function(raw) {
  if (!raw) return "";
  let name = String(raw).trim();
  if (!name) return "";
  
  // 1. Remove ALL parenthetical content: "Acme Corp (formerly XYZ)" → "Acme Corp"
  name = name.replace(/\s*\([^)]*\)/g, "");
  
  // 2. Handle DBA / d/b/a / trading as - keep part BEFORE
  let dbaParts = name.split(/\s+(?:d\.?b\.?a\.?|d\/b\/a|trading\s+as|t\/a)\s+/i);
  if (dbaParts.length > 1) name = dbaParts[0].trim();
  
  // 3. Take first part before comma IF second part looks like suffix
  if (name.includes(",")) {
    let parts = name.split(",");
    if (parts.length >= 2) {
      let second = parts[1].trim().toLowerCase();
      if (/^(inc\.?|incorporated|corp\.?|corporation|llc|ltd\.?|limited|gmbh|plc|sa|bv|ag)\.?\s*$/i.test(second)) {
        name = parts[0].trim();
      }
    }
  }
  
  // 4. Remove legal suffixes (comprehensive list)
  let suffixes = "inc\\.?|incorporated|corp\\.?|corporation|company|co\\.?|llc|l\\.l\\.c\\.?|llp|l\\.l\\.p\\.?|lp|l\\.p\\.?|ltd\\.?|limited|plc|p\\.l\\.c\\.?|holdings?|enterprises?|group|intl\\.?|international|gmbh|g\\.m\\.b\\.h\\.?|ag|a\\.g\\.?|kg|k\\.g\\.?|ohg|ug|sarl|s\\.a\\.r\\.l\\.?|sas|s\\.a\\.s\\.?|sa|s\\.a\\.?|snc|sci|s\\.l\\.?|sl|ltda\\.?|cia\\.?|spa|s\\.p\\.a\\.?|srl|s\\.r\\.l\\.?|bv|b\\.v\\.?|nv|n\\.v\\.?|bvba|cvba|ab|a\\.b\\.?|as|a\\.s\\.?|oy|oyj|aps|s\\.r\\.o\\.?|sro|spol\\.?\\s*s\\s*r\\.?\\s*o\\.?|pte\\.?\\s*ltd\\.?|pty\\.?\\s*ltd\\.?|pvt\\.?\\s*ltd\\.?|kk|k\\.k\\.?|kabushiki\\s*kaisha|gk|g\\.k\\.?|pty|proprietary|pvt\\.?|private|psc|pc|pllc|professional";
  name = name.replace(new RegExp("\\s*(?:and|&)?\\s*\\b(" + suffixes + ")\\.?\\b", "gi"), "");
  
  // 5. Remove "The" from beginning
  name = name.replace(/^the\s+/i, "");
  
  // 6. Clean special chars (keep letters, numbers, spaces, &, -, ', .)
  name = name.replace(/[^\w\s&\-'.]/g, " ");
  
  // 7. Remove trailing junk (&, -, commas, periods)
  name = name.replace(/[\s&\-,\.]+$/, "");
  
  // 8. Normalize whitespace
  name = name.replace(/\s+/g, " ").trim();
  if (!name) return "";
  
  // 9. Remove trailing dots
  name = name.replace(/\.+$/, "").trim();
  
  // 10. Smart Title Case
  let knownAcronyms = new Set(["IBM", "BMW", "SAP", "AWS", "USA", "UK", "AI", "IT", "HR", "CEO", "CFO", "CTO", "VP", "3M"]);
  let lowercaseWords = new Set(["and", "or", "the", "a", "an", "of", "for", "to", "in", "on", "at", "by"]);
  let allCapsInput = name === name.toUpperCase();
  
  let words = name.split(" ");
  let result = words.map((word, i) => {
    let upper = word.toUpperCase();
    
    // Known acronym
    if (knownAcronyms.has(upper)) return upper;
    
    // Short word with & (AT&T, H&M)
    if (word.includes("&") && word.length <= 5) return upper;
    
    // If entire input was ALL CAPS, title case everything
    if (allCapsInput) {
      if (lowercaseWords.has(word.toLowerCase()) && i > 0) return word.toLowerCase();
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    }
    
    // Mixed case - preserve (McDonald's, iPhone)
    if (word !== upper && word !== word.toLowerCase()) return word;
    
    // ALL CAPS short word - might be acronym
    if (word === upper && word.length <= 4) return word;
    
    // ALL CAPS long word - title case
    if (word === upper) return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    
    // Default
    return word.charAt(0).toUpperCase() + word.slice(1);
  });
  
  return result.join(" ");
})({{Org}})
