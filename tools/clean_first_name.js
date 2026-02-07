// Improved First Name Cleaner v2
// For use in Clay formulas - replace {{First Name}} with your column reference

(function(raw) {
  if (!raw) return "";
  let name = String(raw).trim();
  if (!name) return "";
  
  // 1. Check for parenthetical preferred name: "John (Johnny)" → "Johnny"
  let parenMatch = name.match(/\(([^)]+)\)/);
  if (parenMatch) {
    name = parenMatch[1].trim();
  }
  // 2. Check for quoted preferred name: "Nick" John → Nick
  else if (/["'""'']/.test(name)) {
    let quoteMatch = name.match(/["'""'']([^"'""'']+)["'""'']/);
    if (quoteMatch) name = quoteMatch[1].trim();
  }
  
  // 3. Check for Dr./Doctor prefix
  let drPrefix = "";
  let drMatch = name.match(/^\s*(dr\.?|doctor)\s+/i);
  if (drMatch) {
    drPrefix = "Dr. ";
    name = name.slice(drMatch[0].length).trim();
  }
  
  // 4. Remove emojis/special chars (keep letters incl accented, space, apostrophe, hyphen, period)
  name = name.replace(/[^\p{L}\s'\-.']/gu, " ");
  
  // 5. Normalize whitespace
  name = name.replace(/\s+/g, " ").trim();
  if (!name) return "";
  
  // 6. Split and find first real word (skip single-letter initials and suffixes)
  let words = name.split(" ");
  let suffixes = new Set(["jr", "jr.", "sr", "sr.", "ii", "iii", "iv", "v"]);
  let realWords = words.filter(w => !(/^[A-Za-z]\.?$/.test(w)) && !suffixes.has(w.toLowerCase()));
  if (!realWords.length) realWords = words;
  
  let firstName = realWords[0] || "";
  if (!firstName) return "";
  
  // 7. Title case (handle hyphens: Mary-Jane, apostrophes: O'Brien)
  function titleCase(word) {
    if (word.includes("-")) {
      return word.split("-").map(p => p.charAt(0).toUpperCase() + p.slice(1).toLowerCase()).join("-");
    }
    if (/['']/.test(word)) {
      // O'Brien → O'Brien (capitalize after apostrophe)
      return word.split(/([''])/).map((part, i, arr) => {
        if (part === "'" || part === "'") return part;
        return part.charAt(0).toUpperCase() + part.slice(1).toLowerCase();
      }).join("");
    }
    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
  }
  
  return drPrefix + titleCase(firstName);
})({{First Name}})
