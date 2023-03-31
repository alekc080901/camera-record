<template>
<img :src="require('@/assets/minus.svg')" width="20">
</template>

<script>
export default {
    name: 'RemoveButton',
}
</script>

<style scoped>
img {
    width: 38px;
    height: 38px;
    border: 1px solid #ced4da;
    transition: all 0.5s ease;
    border-radius: 0 4px 4px 0;
    cursor: pointer;
}

img:hover {
    border-color: #aaaeb7;
}
</style>
