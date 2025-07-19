const { v4: uuidv4 } = require('uuid');

class MonsterManager {
  constructor(map, playersMap, io) {
    this.monsters = new Map();
    this.map = map;
    this.playersMap = playersMap; // <== Map 구조로
    this.io = io;
  }

  spawnZombie(x, y) {
    const monsterId = uuidv4();
    const newZombie = {
      id: monsterId,
      type: 'zombie',
      position: { x, y },
      hp: Math.floor(Math.random() * 3) + 1,
      damage: 2.5,
      speed: 1000, // ms per move
    };
    this.monsters.set(monsterId, newZombie);
    console.log(`🧟 Zombie spawned at (${x}, ${y})`);
    return newZombie;
  }

  getMonsters() {
    return Array.from(this.monsters.values());
  }

  moveMonsters() {
    for (const monster of this.monsters.values()) {
      const directions = ['up', 'down', 'left', 'right'];
      const direction = directions[Math.floor(Math.random() * directions.length)];
      
      const newPosition = this.calculateNewPosition(monster.position, direction);

      if (this.isValidMove(newPosition)) {
        monster.position = newPosition;

        this.io.emit('monster-moved', {
          id: monster.id,
          position: monster.position,
          type: monster.type
        });
      }
    }
  }

  attackPlayers() {
    for (const monster of this.monsters.values()) {
      for (const player of this.playersMap.values()) { // 맵의 값들을 순회
        const dx = Math.abs(monster.position.x - player.position.x);
        const dy = Math.abs(monster.position.y - player.position.y);
        const distance = dx + dy;

        if (distance <= 1) {
          // 💥 공격 이벤트 발생
          this.io.emit('monster-attacking', { monsterId: monster.id });

          player.health -= monster.damage;
          if (player.health < 0) player.health = 0;

          console.log(`💥 ${monster.type}이(가) ${player.username}을(를) 공격! 데미지: ${monster.damage.toFixed(1)} → 체력: ${player.health.toFixed(1)}`);

          this.io.to(player.playerId).emit('player-damaged', {
            damage: monster.damage,
            newHealth: player.health
          });
        }
      }
    }
  }

  damageMonster(monsterId, damage) {
    const monster = this.monsters.get(monsterId);
    if (!monster) return;

    monster.hp -= damage;
    console.log(`⚔️ 몬스터 ${monsterId}에게 ${damage} 피해 → 남은 HP: ${monster.hp}`);

    if (monster.hp <= 0) {
      this.monsters.delete(monsterId);
      console.log(`☠️ 몬스터 ${monsterId} 사망`);

      // 클라이언트에 몬스터 죽음 알림
      this.io.emit('monster-died', { id: monsterId });
    } else {
      // 체력 변화만 전송
      this.io.emit('monster-damaged', {
        id: monsterId,
        newHp: monster.hp
      });
    }
  }

  calculateNewPosition(currentPos, direction) {
    const { x, y } = currentPos;
    switch (direction) {
      case 'up': return { x, y: y - 1 };
      case 'down': return { x, y: y + 1 };
      case 'left': return { x: x - 1, y };
      case 'right': return { x: x + 1, y };
      default: return currentPos;
    }
  }

  isValidMove(pos) {
    const { x, y } = pos;
    const map = this.map;

    if (x < 0 || x >= this.map.width || y < 0 || y >= this.map.height) {
      return false;
    }
    
    const cell = map.cells[y]?.[x];
    if (!cell || cell.type !== 'grass') return false;
    
    const isOccupied =
      Array.from(this.players.values()).some(p => p.position.x === x && p.position.y === y) ||
      Array.from(this.monsters.values()).some(m => m.position.x === x && m.position.y === y);

    return !isOccupied;
  }
}

module.exports = MonsterManager;
