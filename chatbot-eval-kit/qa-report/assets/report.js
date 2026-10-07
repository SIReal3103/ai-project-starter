const cards = [...document.querySelectorAll('.case-card')];
const query = document.querySelector('#query');
const group = document.querySelector('#group');
const status = document.querySelector('#status');
function filterCases() {
  const term = query.value.normalize('NFC').toLocaleLowerCase('vi');
  cards.forEach(card => { card.hidden = !((group.value === 'all' || card.dataset.group === group.value) && (status.value === 'all' || card.dataset.status === status.value) && card.textContent.normalize('NFC').toLocaleLowerCase('vi').includes(term)); });
  const count = cards.filter(card => !card.hidden).length;
  document.querySelector('#visible-count').textContent = `${count}/${cards.length} phiếu đang hiển thị`;
  document.querySelector('#no-results').hidden = count !== 0;
}
[query, group, status].forEach(control => control.addEventListener('input', filterCases));
document.querySelector('#expand').addEventListener('click', () => {
  const visible = cards.filter(card => !card.hidden);
  const open = visible.some(card => !card.open);
  visible.forEach(card => { card.open = open; });
  document.querySelector('#expand').textContent = open ? 'Thu gọn phiếu' : 'Mở toàn bộ phiếu';
});
let printState;
window.addEventListener('beforeprint', () => {
  printState = [...document.querySelectorAll('details')].map(el => ({el, open:el.open, hidden:el.hidden}));
  printState.forEach(({el}) => { el.open = true; el.hidden = false; });
});
window.addEventListener('afterprint', () => { if (printState) printState.forEach(({el,open,hidden}) => { el.open = open; el.hidden = hidden; }); });
document.querySelector('#print').addEventListener('click', () => window.print());
filterCases();
