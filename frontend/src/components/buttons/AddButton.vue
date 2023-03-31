<template>
    <svg fill="#202020" width="800px" height="800px" viewBox="0 0 24 24" version="1.2" baseProfile="tiny" xmlns="http://www.w3.org/2000/svg"><path d="M18 10h-4v-4c0-1.104-.896-2-2-2s-2 .896-2 2l.071 4h-4.071c-1.104 0-2 .896-2 2s.896 2 2 2l4.071-.071-.071 4.071c0 1.104.896 2 2 2s2-.896 2-2v-4.071l4 .071c1.104 0 2-.896 2-2s-.896-2-2-2z"/></svg>
</template>

<script>
export default {
    name: 'AddButton',
}
</script>

<style scoped>
svg {
    width: 30px;
    height: 30px;
    transition: all 0.3s ease;
    cursor: pointer;
}

svg:hover {
    fill: rgb(90, 88, 88);
}

img:hover {
    border-color: #aaaeb7;
}
</style>
