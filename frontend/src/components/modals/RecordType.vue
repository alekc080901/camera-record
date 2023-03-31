<template>
<GDialog>
    <template #activator="{ onClick }">
        <RecordButton class="add-button" @click="onClick" />
    </template>
    <template #default="{onClose}">
        <ModalToolbar msg="Тип записи" @close="onClose"/>
        
        <div class="container p-4">
            <div class="row">
                <AddRecordModal/>
                <AddRegularRecordModal/>
            </div>
        </div>
    </template>
    
</GDialog>
</template>

<script>
import AddRecord from './AddRecord.vue';
import AddRegularRecord from './AddRegularRecord.vue';
import RecordButton from '../buttons/RecordButton.vue';
import 'gitart-vue-dialog/dist/style.css'
import {
    GDialog
} from 'gitart-vue-dialog'
import ModalToolbar from './ModalToolbar.vue'

export default {
    name: 'RecordType',
    components: {
        ModalToolbar,
        GDialog,
        AddRecordModal: AddRecord,
        AddRegularRecordModal: AddRegularRecord,
        RecordButton,
    }
};
</script>

<style>
.add-button {
    width: 100px;
    height: 100px;
    cursor: pointer;
}

.record-type {
    width: 200px;
    height: 135px;
    cursor: pointer;
}
</style>
