// Redacta secretos reales (tokens de join LXD/microOVN, claves WireGuard)
// de los .md exportados, antes de guardarlos en el repositorio.
const fs = require('fs');
const path = require('path');

const SRC = path.join(__dirname, 'output');
const DST = path.join(__dirname, 'sanitized');

const WG_KEYS = {
  'yGSOm1a4aQE2d0Ai9n6QhDZ+s7l3G1Jg+CBp0vI6qFQ=': '<CLAVE_PUBLICA_WIREGUARD_PFR1>',
  'e0VHCkhlFR6rnO3ZAyqAn+2nYolz544mtZ/FDSGbT1I=': '<CLAVE_PUBLICA_WIREGUARD_CAR1>',
};

function redact(content) {
  let out = content;
  // Tokens tipo JWT/base64 largos generados por lxd/microovn (join tokens,
  // pending identity tokens). Suelen empezar con "eyJ" (base64 de '{"') y
  // tener 80+ caracteres sin espacios.
  out = out.replace(/eyJ[A-Za-z0-9+/=]{60,}/g, '<TOKEN_REDACTADO_LXD_MICROOVN>');
  // Claves publicas WireGuard conocidas (reemplazo literal)
  for (const [key, placeholder] of Object.entries(WG_KEYS)) {
    out = out.split(key).join(placeholder);
  }
  return out;
}

function walk(srcDir, dstDir) {
  fs.mkdirSync(dstDir, { recursive: true });
  for (const entry of fs.readdirSync(srcDir, { withFileTypes: true })) {
    const srcPath = path.join(srcDir, entry.name);
    const dstPath = path.join(dstDir, entry.name);
    if (entry.isDirectory()) {
      walk(srcPath, dstPath);
    } else if (entry.name.endsWith('.md')) {
      const content = fs.readFileSync(srcPath, 'utf-8');
      fs.writeFileSync(dstPath, redact(content), 'utf-8');
    }
  }
}

walk(SRC, DST);
console.log('Sanitizado en:', DST);

// Verificación: buscar cualquier resto sospechoso de token/clave sin redactar
let warnings = 0;
function verify(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) { verify(p); continue; }
    if (!entry.name.endsWith('.md')) continue;
    const content = fs.readFileSync(p, 'utf-8');
    if (/eyJ[A-Za-z0-9+/=]{20,}/.test(content)) {
      console.log('  [!] posible token sin redactar en', p);
      warnings++;
    }
    for (const key of Object.keys(WG_KEYS)) {
      if (content.includes(key)) {
        console.log('  [!] clave WireGuard sin redactar en', p);
        warnings++;
      }
    }
  }
}
verify(DST);
console.log(warnings === 0 ? 'Verificación OK: no quedaron tokens/claves sin redactar.' : `Atención: ${warnings} advertencias.`);
