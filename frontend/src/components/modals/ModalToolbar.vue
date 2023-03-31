<template>
<div class="modal-header ps-5 pe-5">
    <h3 class="header-message">{{ msg }}</h3>
    <button type="button" class="btn-close modal-close-button" aria-label="Close" @click="onClose"></button>
</div>
</template>

<script>
export default {
    name: 'ModalToolbar',
    props: {
        msg: String
    },
    emits: ['close'],

    setup(_, {
        emit
    }) {
        const onClose = () => {
            emit('close')
        }

        return {
            onClose,
        }
    },
}
</script>

<style>
.modal-header {
    position: relative;
    display: flex;
    justify-content: center;
    padding-top: 7px;
    box-shadow: 0px 17px 50px -4px rgba(34, 60, 80, 0.2);
}

.header-message {
    font-weight: bold;
}

.modal-close-button {
    position: absolute;
    top: 8px;
    right: 8px;
    font-size: 20px;
}
</style>
