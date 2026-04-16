<template>
  <div class="home-page">
    <HeroBanner />
    <QuickEntry />

    <!-- 公告 + 侧边面板 -->
    <section class="content-section">
      <div class="content-inner">
        <div class="main-col">
          <AnnouncementBoard />
        </div>
        <div class="side-col">
          <SidePanel />
        </div>
      </div>
    </section>

    <DiaryPreview />
    <OnlineResources />
    <ContactSection />
    <SiteFooter />
  </div>
</template>

<script setup>
import HeroBanner       from '@/components/HeroBanner.vue'
import QuickEntry       from '@/components/QuickEntry.vue'
import AnnouncementBoard from '@/components/AnnouncementBoard.vue'
import SidePanel        from '@/components/SidePanel.vue'
import OnlineResources  from '@/components/OnlineResources.vue'
import DiaryPreview     from '@/components/DiaryPreview.vue'
import ContactSection   from '@/components/ContactSection.vue'
import SiteFooter       from '@/components/SiteFooter.vue'
</script>

<style scoped>
.home-page { background: #f4f7fc; }

.content-section {
  padding: 40px 0 48px;
}
.content-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
  align-items: start;
}
</style>
