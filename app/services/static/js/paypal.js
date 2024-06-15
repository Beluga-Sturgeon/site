paypal.Buttons({

    style: {
        layout: 'vertical',
        height: 55,
        width: 50,
        shape: 'rect',
        label: 'paypal',
        color: 'silver'
    },
    
    // Sets up the transaction when a payment button is clicked
    createOrder: (data, actions) => {
        return actions.order.create({
            purchase_units: [{
                amount: {
                    value: '3.00' // Can also reference a variable or function
                }
            }]
        });
    },
    // Finalize the transaction after payer approval
    // Finalize the transaction on the server after payer approval
    onApprove: (data, actions) => {
        return fetch(`/payment/${data.orderID}/capture`, {
            method: "post",
        })
            .then((response) => response.json())
            .then((orderData) => {
                // Successful capture! For dev/demo purposes:
                console.log('Capture result', orderData, JSON.stringify(orderData, null, 2));

                if (orderData.status = "COMPLETED"){
                    window.location.href = "/portfolio"
                }
            });
    }
}).render('#paypal-button-container');