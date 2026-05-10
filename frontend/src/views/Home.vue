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
import HeroBanner        from '@/components/HeroBanner.vue'
import QuickEntry        from '@/components/QuickEntry.vue'
import AnnouncementBoard from '@/components/AnnouncementBoard.vue'
import SidePanel         from '@/components/SidePanel.vue'
import OnlineResources   from '@/components/OnlineResources.vue'
import DiaryPreview      from '@/components/DiaryPreview.vue'
import ContactSection    from '@/components/ContactSection.vue'
import SiteFooter        from '@/components/SiteFooter.vue'
</script>

<style scoped>
.home-page { background: var(--c-beige); }

.content-section {
  padding: var(--sp-12) 0 var(--sp-16);
}

.content-inner {
  max-width: var(--container);
  margin: 0 auto;
  padding: 0 var(--sp-6);
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: var(--sp-6);
  align-items: start;
}

@media (max-width: 1024px) {
  .content-inner {
    grid-template-columns: 1fr;
  }
}
</style>
