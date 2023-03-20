<template>
<img :src="require('@/assets/logo.svg')" :width="size.width" :height="size.height">
</template>

<script>
export default {
    name: 'RecordButton',
    props: {
        img: String,
        size: Object,
    },
}
</script>

<style scoped></style>
