// 마인크래프트 스타일 맵 생성기 (내구도 시스템)
class MapGenerator {
  constructor(width = 50, height = 50) {
    this.width = width;
    this.height = height;
  }

  generateMap() {
    const map = [];
    
    for (let y = 0; y < this.height; y++) {
      const row = [];
      for (let x = 0; x < this.width; x++) {
        row.push(this.generateCell(x, y));
      }
      map.push(row);
    }
    
    return {
      width: this.width,
      height: this.height,
      cells: map
    };
  }

  generateCell(x, y) {
    const random = Math.random();
    
    // 가장자리는 무조건 돌 (경계 역할)
    if (x === 0 || x === this.width - 1 || y === 0 || y === this.height - 1) {
      return {
        type: 'stone',
        maxDurability: 5,
        currentDurability: 5,
        miningProgress: 0,
        resources: 3
      };
    }
    
    // 새로운 자원 분포 비율
    if (random < 0.65) {        // 65% 잔디
      return {
        type: 'grass',
        maxDurability: 1,
        currentDurability: 1,
        miningProgress: 0,
        resources: 0
      };
    } else if (random < 0.75) { // 10% 나무 (3타)
      return {
        type: 'tree',
        maxDurability: 3,
        currentDurability: 3,
        miningProgress: 0,
        resources: Math.floor(Math.random() * 3) + 2
      };
    } else if (random < 0.90) { // 15% 돌 (5타)
      return {
        type: 'stone',
        maxDurability: 5,
        currentDurability: 5,
        miningProgress: 0,
        resources: Math.floor(Math.random() * 3) + 2
      };
    } else if (random < 0.97) { // 7% 철광석 (8타)
      return {
        type: 'iron_ore',
        maxDurability: 8,
        currentDurability: 8,
        miningProgress: 0,
        resources: Math.floor(Math.random() * 2) + 1
      };
    } else {                    // 3% 다이아몬드 (12타)
      return {
        type: 'diamond',
        maxDurability: 12,
        currentDurability: 12,
        miningProgress: 0,
        resources: 1
      };
    }
  }
}

module.exports = MapGenerator;