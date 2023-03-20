<template>
<BaseModal>
    <template #test="{ onClose }">
        <button @click="onClose">Не тестик</button>
    </template>
     <template #activator="{ onClick }">
        <RecordButton class="col" img="./assets/logo.svg" :size="{width: 110, height:110}" @click="onClick"/>
    </template>
    <!--<template v-slot:header>
        <h3>Добавление отложенной записи</h3>
    </template>
    <template #body="{ onClose }">
        <form>
            <div class="container mb-3">
                <div class="form-group m-2">
                    <label for="record-name">Название записи</label>
                    <input type="text" class="form-control" id="record-name" placeholder="Олег" required>
                </div>
                <div class="form-group m-2">
                    <label for="record-rtsp">RTSP</label>
                    <input type="text" class="form-control" id="record-rtsp" placeholder="rtsp://" required>
                </div>
                <div class="form-group m-2">
                    <label for="record-fpm">Кадров в минуту</label>
                    <input type="number" class="form-control" id="record-fpm" placeholder="1200" required>
                </div>
                <div class="form-group m-2 mb-3">
                    <label for="record-comment">Комментарий</label>
                    <textarea class="form-control" id="record-comment" rows="2" placeholder="Текст комментария"></textarea>
                </div>

                <div class="row">
                    <button class="col btn btn-primary m-2" type="submit" >Начать запись</button>
                    <button class="col btn btn-secondary m-2" type="button" @click="onClose">Отмена</button>
                </div>
                
            </div>
        </form>
    </template> -->
</BaseModal>
</template>

<script>
import Base from './Base.vue';
import RecordButton from '../buttons/RecordButton.vue';

export default {
    name: 'ModalFrame',
    components: {
        BaseModal: Base,
        RecordButton,
    }
};
</script>

<style scoped>
h3 {
    text-align: center;
}
</style>
