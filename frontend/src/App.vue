<template>
<GDialogRoot />
<RecordTypeModal />
<TaskTable />
</template>

<script>
import RecordType from './components/modals/RecordType.vue';
import TaskTable from './components/TaskTable.vue';
import {
    GDialogRoot
} from 'gitart-vue-dialog'

export default {
    name: 'App',
    components: {
        TaskTable,
        RecordTypeModal: RecordType,
        GDialogRoot,
    }
}
</script>

<style>
body {
    font-family: Avenir, Helvetica, Arial, sans-serif;
}

#app {
    text-align: center;
    color: #2c3e50;
    margin-top: 10px;
}

.logo {
    height: 100px;
}

.g-dialog-content {
  width: max-content;
}

.dp__input {
    border-radius: 4px 0 0 4px !important;
}
</style>

