if(document.getElementById) {
  var wrapper = document.getElementById('visual-portal-wrapper');
  var content = document.getElementById('portal-column-content');
  if(content) {
    String.prototype.trim = function() {
      return this.replace(/^\s+|\s+$/g,'');
    }
    var sl = document.getElementById('portal-column-one');
    var sr = document.getElementById('portal-column-two');
    sl = sl && sl.innerHTML.trim();
    sr = sr && sr.innerHTML.trim();
    wrapper.className = (sl && sr && 'sl sr') || (sl && 'sl') || (sr && 'sr') || '';
    content.className = (sl && sr && 'sl sr') || (sl && 'sl') || (sr && 'sr') || '';
  }
}