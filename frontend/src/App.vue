<template>

<RecordTypeModal />
<TaskTable />
</template>

<script>
import RecordType from './components/modals/RecordType.vue';
import TaskTable from './components/TaskTable.vue';

export default {
    name: 'App',
    components: {
        TaskTable,
        RecordTypeModal: RecordType,
    }
}
</script>

<style>
#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    text-align: center;
    color: #2c3e50;
    margin-top: 10px;
}

.logo {
    height: 100px;
}
</style>

<style scoped>
.wrapper {
  color: #000;
}

.content {
  padding: 20px;
}

.title {
  font-size: 30px;
  font-weight: 700;
  margin-bottom: 20px;
}

.actions {
  display: flex;
  justify-content: flex-end;
  padding: 10px 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.12);
}
</style>
