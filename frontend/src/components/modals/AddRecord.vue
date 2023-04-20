<template>
<GDialog>
    <template #activator="{ onClick }">
        <img class="record-type" :src="require('@/assets/delayed.png')" @click="onClick" />
    </template>

    <template #default="{ onClose }">
        <ModalToolbar msg="Добавление отложенной записи" @close="onClose" />
        <form class="add-form" name="add-delayed" @submit="sendForm">
            <div class="container mb-3">
                <div class="form-group m-2">
                    <label for="record-name">Название записи</label>
                    <input type="text" name="name" title="name" class="form-control" id="record-name" placeholder="Олег" v-model="name" required>
                </div>

                <div class="form-group m-2">
                    <label for="record-rtsp">RTSP</label>
                    <input type="text" name="rtsp" title="rtsp" class="form-control" id="record-rtsp" placeholder="rtsp://" required>
                </div>

                <div class="form-group m-2">
                    <label for="record-rtsp">Директория</label>
                    <input type="text" name="path" title="directory" class="form-control" id="record-path" placeholder="videos/Friday" v-model="directory">
                </div>

                <div class="form-group m-2 mb-1">
                    <label for="record-fpm">Кадров в минуту</label>
                    <input type="number" name="fpm" title="fpm" class="form-control" id="record-fpm" placeholder="1200" v-model="fpm" :disabled="audioChecked || nativeFpmChecked" required>
                </div>
                <div class="form-check m-2 mb-3">
                    <label for="record-native-fpm">Использовать параметры камеры</label>
                    <input type="checkbox" class="form-check-input" name="native-fpm" title="native-fpm" id="record-native-fpm" v-model="nativeFpmChecked">
                </div>

                <div class="form-group m-2 mb-3">
                    <label for="record-comment">Комментарий</label>
                    <textarea class="form-control" name="comment" title="comment" id="record-comment" rows="2" placeholder="Текст комментария"></textarea>
                </div>

                <div class="form-group m-2 mb-3">
                    <label for="record-date-0">Дата</label>
                    <div class="dates">
                        <div class="date-input" v-for="(_, id) in dateComponents" :key="id">
                            <DateTimeInput class="mb-2" name="date" :id="`record-date-${id}}`" />
                            <RemoveButton class="button-delete" :id="`del-${id}`" @click="removeDateInput" />
                        </div>
                        <AddButton class="button-add" @click="addNewDateInput" />
                    </div>
                </div>

                <div class="form-check m-2 mb-3">
                    <label for="record-audio">Записывать аудиодорожку</label>
                    <input type="checkbox" class="form-check-input" name="audio" title="audio" id="record-audio" v-model="audioChecked" >
                </div>

                <div class="row m-2">
                    <button class="col btn btn-primary m-2" type="submit">Начать запись</button>
                    <button class="col btn btn-secondary m-2" type="button" @click="onClose">Отмена</button>
                </div>

                <div v-if="formSendError" style="white-space: pre-line" class="alert alert-danger" role="alert">
                    {{ formSendErrorMessage }}
                </div>
            </div>
        </form>
    </template>
</GDialog>
</template>

<script>
import ModalToolbar from './ModalToolbar.vue';
import DateTimeInput from '../inputs/DateTimeInput.vue';
import AddButton from '../buttons/AddButton.vue';
import RemoveButton from '../buttons/RemoveButton.vue';

import 'gitart-vue-dialog/dist/style.css'
import {
    GDialog
} from 'gitart-vue-dialog'

export default {
    name: 'AddRecord',
    components: {
        GDialog,
        ModalToolbar,
        DateTimeInput,
        AddButton,
        RemoveButton,
    },
    data() {
        return {
            count: 0,
            dateComponents: [0],

            name: localStorage.getItem('delayedName'),
            fpm: localStorage.getItem('delayedFPM'),
            directory: localStorage.getItem('delayedDir'),

            formSendError: false,
            formSendErrorMessage: '',

            audioChecked: false,
            nativeFpmChecked: false,
        }
    },
    methods: {
        addNewDateInput() {
            this.count++;
            this.dateComponents.push(this.count);
        },
        removeDateInput(e) {
            if (this.dateComponents.length <= 1)
                return

            const inputIdx = Number(e.target.id.split('-').at(-1));
            this.dateComponents = this.dateComponents.filter((e) => e !== inputIdx);
        },

        considerTimezone(date) {
            const hoursDiff = date.getHours() - date.getTimezoneOffset() / 60;
            date.setHours(hoursDiff);
            return date;
        },
        parseDateRange(dateString) {
            const parseDate = (datetime) => {
                const [date, time] = datetime.split(', ')
                const [day, month, year] = date.split('-');
                const [hours, minutes] = time.split(':')

                return new Date(+year, +month - 1, +day, +hours, +minutes)
            }

            const [dateFrom, dateTo] = dateString.split(' – ')
            return {
                date_from: this.considerTimezone(parseDate(dateFrom)).toISOString(),
                date_to: this.considerTimezone(parseDate(dateTo)).toISOString(),
            }
        },
        getDates(form) {
            const dates = form.date;
            if (dates.constructor === HTMLInputElement)
                return [this.parseDateRange(dates.value)];

            return [...dates].map(e => this.parseDateRange(e.value));
        },
        async sendForm(e) {
            e.preventDefault();
            const form = document.forms['add-delayed'];
            const jsonBody = {
                name: form.name.value,
                rtsp_url: form.rtsp.value,
                comment: form.comment.value,
                path: form.path.value,
                intervals: this.getDates(form),
                config: {
                    audio: form.audio.checked
                },
            }

            if (!form.fpm.disabled)
                jsonBody.fpm = form.fpm.value

            await fetch('http://127.0.0.1:8000/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(jsonBody),
                })
                .then(async response => {
                    if (response.status >= 200 && response.status < 300) {
                        this.formSendError = false;

                        localStorage.setItem('delayedName', jsonBody.name);
                        localStorage.setItem('delayedFPM', jsonBody.fpm);
                        localStorage.setItem('delayedDir', jsonBody.path);

                        window.location.reload();
                        return response.json();
                    }
                    let error = response.status === 422 ?
                        new Error(JSON.stringify((await response.json())['detail'][0], null, 2)) :
                        new Error();
                    error.response = response;
                    throw error;
                })
                .catch(e => {
                    console.log(e);
                    this.formSendError = true;
                    this.formSendErrorMessage = e.response === undefined ? 'Невозможно подключиться к серверу' :
                        `${e.response.status} ${e.response.statusText}\n${e.message}`;
                })
        }
    }
};
</script>

<style scoped>
.date-input {
    display: flex;
    flex-direction: row;
    position: relative;
}

.dp__theme_light {
    --dp-border-color: #ced4da;
}

.dates {
    display: flex;
    flex-direction: column;
    justify-content: center;
    justify-items: center;
}

.button-add {
    align-self: center;
}
</style>
