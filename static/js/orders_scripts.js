window.onload = function () {
    let _quantity, _price, orderitem_num, delta_quantity, orderitem_quantity, delta_cost;
    let quantity_arr = [];
    let price_arr = [];

// узнаем число форм в наборе
    let TOTAL_FORMS = parseInt($('input[name="orderitems-TOTAL_FORMS"]').val());

// получаем значения обычных текстовых элементов DOM модели при помощи метода «.text()​»​
    let order_total_quantity = parseInt($('.order_total_quantity').text()) || 0;
    let order_total_cost = parseFloat($('.order_total_cost').text().replace(',', '.')) || 0;

    for (let i = 0; i < TOTAL_FORMS; i++) {
        _quantity = parseInt($('input[name="orderitems-' + i + '-quantity"]').val());
        _price = parseFloat($('.orderitems-' + i + '-price').text().replace(',', '.'));
        quantity_arr[i] = _quantity;
        if (_price) {
            price_arr[i] = _price;
        } else {
            price_arr[i] = 0;
        }
    }

    //Если на странице данных о количестве товаров в заказе нет (например, при создании нового заказа) - вычисляем
    //значения «order_total_quantity​» и «order_total_cost​»​, а затем выводим их на экран при помощи jQuery метода «​.html()​».
    if (!order_total_quantity) {
        orderSummaryRecalc();
    }

    // обрабатываем событие изменения количества товаров в заказе при помощи jQuery метода «.on()»
    $('.order_form').on('click', 'input[type="number"]', function () {
        // Получаем объект-источник события из глобального объекта события «​event​»​:
        let target = event.target;
        // Из имени объекта (​target.name​) получаем номер элемента в списке форм (orderitems-1-quantity)
        orderitem_num = parseInt(target.name.replace('orderitems-', '').replace('-quantity', ''));
        if (price_arr[orderitem_num]) {
            orderitem_quantity = parseInt(target.value);
            delta_quantity = orderitem_quantity - quantity_arr[orderitem_num];
            quantity_arr[orderitem_num] = orderitem_quantity;
            orderSummaryUpdate(price_arr[orderitem_num], delta_quantity);
        }
    });

    // для корректного обновления статистики при добавлении новых элементов в заказ
    $('.order_form select').change(function () {
        let target = event.target;
        orderitem_num = parseInt(target.name.replace('orderitems-', '').replace('-product', ''));
        // Django, при формировании выпадающего списка с продуктами, автоматически заполняет атрибут «val» каждого
        // элемента значением «pk» из базы данных. Сохраняем это значение в переменную «​orderitem_product_pk»​ и делаем
        // запрос цены контроллеру через «.ajax()».
        let orderitem_product_pk = target.options[target.selectedIndex].value;

        if (orderitem_product_pk) {
            $.ajax({
                url: "/order/product/" + orderitem_product_pk + "/price/",
                success: function (data) {
                    if (data.price) {
                        price_arr[orderitem_num] = parseFloat(data.price);
                        if (isNaN(quantity_arr[orderitem_num])) {
                            quantity_arr[orderitem_num] = 0;
                        }
                        let price_html = '<span>' + data.price.toString().replace('.', ',') + '</span>руб';
                        // Получаем значение цены
                        let current_tr = $('.order_form table').find('tr:eq(' + (orderitem_num + 1) + ')');

                        // В массив «price_arr» заносим полученное в ответе значение цены и выводим на странице
                        current_tr.find('td:eq(2)').html(price_html);

                        if (isNaN(current_tr.find('input[type="number"]').val())) {
                            current_tr.find('input[type="number"]').val(0);
                        }
                        orderSummaryRecalc();
                    }
                    console.log('ajax done');
                },
            });
        }
    });

    // благодаря подключенному файлу «jquery.formset.js», получаем новый метод «.formset()» для объектов jQuery в скриптах.
    // В него, по аналогии с «.ajax()», передаем JSON объект с параметрами:
    $('.formset_row').formset({
        addText: 'добавить продукт', // добавляем кнопку добавления продукта
        deleteText: 'удалить', // добавляем кнопку удаления продукта
        prefix: 'orderitems', // префикс имен элементов на форме (в нашем случае - имя «orderitems» класса модели формы набора)
        removed: deleteOrderItem // имя пользовательской функции-обработчика удаления элемента из набора
    });

    /**
     * Функция удаления продукта (jquery.formset)
     * @param row массив из одной строки, содержащей удаляемую форму набора
     */
    function deleteOrderItem(row) {
        var target_name= row[0].querySelector('input[type="number"]').name;
        orderitem_num = parseInt(target_name.replace('orderitems-', '').replace('-quantity', ''));
        delta_quantity = -quantity_arr[orderitem_num];
        quantity_arr[orderitem_num] = 0;
        if (!isNaN(price_arr[orderitem_num]) && !isNaN(delta_quantity)) {
            orderSummaryUpdate(price_arr[orderitem_num], delta_quantity);
        }
    }

    /**
     * Обновление статики на странице.
     * @param orderitem_price значение цены товара.
     * @param delta_quantity изменение кол-ва товара.
     */
    function orderSummaryUpdate(orderitem_price, delta_quantity) {
        delta_cost = orderitem_price * delta_quantity;

        order_total_cost = Number((order_total_cost + delta_cost).toFixed(2));
        order_total_quantity += delta_quantity;

        $('.order_total_cost').html(order_total_cost.toString());
        $('.order_total_quantity').html(order_total_quantity.toString());
    }

    function orderSummaryRecalc() {
        order_total_quantity = 0;
        order_total_cost = 0;

        for (let i = 0; i < TOTAL_FORMS; i++) {
            order_total_quantity += quantity_arr[i];
            order_total_cost += quantity_arr[i] * price_arr[i];
        }
        $('.order_total_quantity').html(order_total_quantity.toString());
        // Для ​округления​ числового значения используем JS класс-обертку «​Number()​»
        $('.order_total_cost').html(Number(order_total_cost.toFixed(2)).toString());
    }
}