<template>
  <Teleport to="body">
    <dialog ref="dialog" class="temporary-project-dialog" aria-labelledby="temporary-project-title"
      aria-describedby="temporary-project-description" :aria-busy="busy" @cancel.prevent="decline">
      <span class="temporary-project-dialog__eyebrow">临时任务已结束</span>
      <h2 id="temporary-project-title">是否将它添加到项目里？</h2>
      <p id="temporary-project-description">
        以「{{ title }}」创建一个独立项目，保留原任务、计划用时和计时记录。
        重名项目将按原任务创建时间标注（1）（2）。
      </p>
      <p v-if="error" class="temporary-project-dialog__error" role="alert">{{ error }}</p>
      <p v-if="busy" role="status">正在创建项目，请稍候…</p>
      <footer>
        <button type="button" class="button button--quiet" :disabled="busy" autofocus @click="decline">否</button>
        <button type="button" class="button button--primary" :disabled="busy" @click="$emit('accept')">是</button>
      </footer>
    </dialog>
  </Teleport>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps<{ title: string; busy: boolean; error: string }>()
const emit = defineEmits<{ accept: []; decline: [] }>()
const dialog = ref<HTMLDialogElement | null>(null)
function decline(): void {
  if (!props.busy) emit('decline')
}
onMounted(() => dialog.value?.showModal())
onBeforeUnmount(() => dialog.value?.close())
</script>

<style scoped>
.temporary-project-dialog {
  width: min(440px, calc(100vw - 32px));
  max-height: calc(100dvh - 32px);
  overflow: auto;
  padding: 28px;
  border: 1px solid #e6e3f1;
  border-radius: 20px;
  background: #fff;
  color: #252334;
  box-shadow: 0 24px 80px #24203830;
}
.temporary-project-dialog::backdrop { background: #18152466; }
.temporary-project-dialog__eyebrow { color: #7864bb; font-size: 13px; }
.temporary-project-dialog h2 { margin: 12px 0; font-size: 22px; }
.temporary-project-dialog p { line-height: 1.7; overflow-wrap: anywhere; }
.temporary-project-dialog__error { color: #b42318; }
.temporary-project-dialog footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.temporary-project-dialog footer button { min-width: 80px; }
</style>
