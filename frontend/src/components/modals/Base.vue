<template>
<Modal>
    <template #activator="{ onClick }">
        <slot name="activator" @click="onClick">
        </slot>
    </template>

    <template #default="{ onClose }">
        <slot name="test" @click="onClose">
            <button  @click="onClose">Тестик</button>
        </slot>
        <div class="content">
            <div class="modal-header" v-if="hasHeaderSlot">
                <slot class="title" name="header">
                    Header
                </slot>
            </div>

            <div class="modal-body">
                <slot name="body" @click="onClose">
                    <div>
                        Lorem ipsum dolor sit amet consectetur adipisicing
                        elit. Porro, ratione!
                    </div>
                </slot>
            </div>
        </div>
    </template>

</Modal>
</template>

<script>
import 'gitart-vue-dialog/dist/style.css'
import {
    GDialog
} from 'gitart-vue-dialog'

export default {
    name: 'ModalFrame',
    components: {
        Modal: GDialog,
    },
    computed: {
        hasHeaderSlot() {
            return !!this.$slots.header;
        }
    }
};
</script>

<style>
.g-dialog-content {
    width: initial;
}

.modal-backdrop {
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: rgba(0, 0, 0, 0.3);
    display: flex;
    justify-content: center;
    align-items: center;
}

.modal {
    background: #FFFFFF;
    box-shadow: 2px 2px 20px 1px;
    overflow-x: auto;
    display: flex;
    flex-direction: column;
}

.modal-header {
    padding: 15px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.modal-header {
    border-bottom: 1px solid #eeeeee;
    color: #4AAE9B;
}

.modal-body {
    position: relative;
    padding: 20px 10px;
}

.btn-close {
    border: none;
    font-size: 20px;
    padding: 20px;
    cursor: pointer;
    font-weight: bold;
    color: #4AAE9B;
    background: transparent;
}

.btn-green {
    color: white;
    background: #4AAE9B;
    border: 1px solid #4AAE9B;
    border-radius: 2px;
}

.modal-fade-enter,
.modal-fade-leave-active {
    opacity: 0;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
    transition: opacity .5s ease
}
</style>
