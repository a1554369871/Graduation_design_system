<template>
  <div class="stat-card">
    <el-icon :size="36" :color="color"><component :is="icon" /></el-icon>
    <div class="stat-info">
      <span class="stat-value">{{ value }}</span>
      <span class="stat-label">{{ label }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({ icon: String, label: String, value: [Number, String], color: { type: String, default: '#409eff' } })
</script>

<style scoped>
.stat-card { display: flex; align-items: center; gap: 16px; padding: 8px; }
.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 28px; font-weight: bold; line-height: 1.2; }
.stat-label { font-size: 14px; color: #999; }
</style>
