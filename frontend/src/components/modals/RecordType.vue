<template>
<BaseModal>
    <template #activator="{ onClick }">
        <RecordButton class="add-button" img="./assets/logo.svg" :size="{width: 100, height:100}" @click="onClick" />
    </template>
    <template v-slot:header>
        <h3 >Тип записи</h3>
    </template>
    <template v-slot:test="{ onClose }">
        <button @click="this.test(onClodse)">жопа</button>
    </template>
    <template v-slot:body>
        <div class="container">
            <div class="row">
                <AddRecordModal/>
                <AddRecordModal/>
            </div>
        </div>

    </template>
</BaseModal>
</template>

<script>
import Base from './Base.vue';
import AddRecord from './AddRecord.vue';
import RecordButton from '../buttons/RecordButton.vue';

export default {
    name: 'ModalFrame',
    components: {
        BaseModal: Base,
        AddRecordModal: AddRecord,
        RecordButton,
    },
    methods: {
        test(arg) {
            console.log(arg)
        }
    }
};
</script>

<style scoped>
h3 {
    text-align: center;
}
</style>
