<template>
  <section class="treehole-section">
    <div class="inner">
      <div class="section-head">
        <div class="head-left">
          <h2 class="section-title">🕳️ 树洞 · 说出你的心声</h2>
          <p class="section-sub">匿名发声，温暖同行。这里有人在听。</p>
        </div>
        <router-link to="/treehouse" class="enter-btn">进入树洞 →</router-link>
      </div>

      <div class="holes-grid">
        <div v-for="hole in holes" :key="hole.id" class="hole-card">
          <p class="hole-content">{{ hole.content }}</p>
          <div class="hole-footer">
            <span v-for="tag in hole.tags" :key="tag" class="hole-tag">{{ tag }}</span>
            <span class="hole-time">{{ hole.time }}</span>
          </div>
        </div>
      </div>

      <p class="privacy-note">🔒 所有内容匿名发布，经审核后可见，中心老师会关注每一条留言。</p>
    </div>
  </section>
</template>

<script setup>
const holes = [
  {
    id: 1,
    content: '最近论文压力太大了，感觉每天都睡不好，不知道自己还能撑多久。但又不知道跟谁说，怕麻烦别人……',
    tags: ['学业压力'],
    time: '2 小时前',
  },
  {
    id: 2,
    content: '和室友的关系越来越僵，宿舍气氛很压抑。每次回宿舍都很煎熬，不知道要怎么开口和解。',
    tags: ['人际关系'],
    time: '5 小时前',
  },
  {
    id: 3,
    content: '看到周围同学陆续拿到实习 offer，自己投了很多简历却没有回音，开始怀疑自己是不是真的很差。',
    tags: ['就业焦虑'],
    time: '1 天前',
  },
]
</script>

<style scoped>
.treehole-section {
  background: linear-gradient(135deg, #007ab0 0%, #009DE0 100%);
  padding: 56px 0;
}

.inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 32px;
}
.head-left { flex: 1; }
.section-title {
  font-size: 24px;
  font-weight: 700;
  color: white;
  margin: 0 0 8px;
}
.section-sub {
  font-size: 14px;
  color: rgba(255,255,255,0.7);
  margin: 0;
}

.enter-btn {
  display: inline-block;
  background: white;
  color: #009DE0;
  padding: 10px 24px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: transform 0.15s, box-shadow 0.15s;
  white-space: nowrap;
  box-shadow: 0 2px 10px rgba(0,0,0,0.15);
}
.enter-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(0,0,0,0.2); }

.holes-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.hole-card {
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 10px;
  padding: 20px;
  transition: background 0.15s, transform 0.15s;
}
.hole-card:hover {
  background: rgba(255,255,255,0.18);
  transform: translateY(-2px);
}

.hole-content {
  font-size: 14px;
  line-height: 1.75;
  color: rgba(255,255,255,0.92);
  margin: 0 0 14px;
}

.hole-footer {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hole-tag {
  background: rgba(255,255,255,0.2);
  color: rgba(255,255,255,0.88);
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11.5px;
}

.hole-time {
  margin-left: auto;
  font-size: 11.5px;
  color: rgba(255,255,255,0.5);
}

.privacy-note {
  text-align: center;
  font-size: 12.5px;
  color: rgba(255,255,255,0.55);
  margin: 0;
}
</style>
