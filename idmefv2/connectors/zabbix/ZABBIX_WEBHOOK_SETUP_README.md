## Zabbix Webhook Setup (Push Mode)

To use the connector in **push** mode, configure Zabbix to send alerts via a **custom Webhook Media Type**.

### Step 1 – Create a new Media Type

1. Go to **Alerts → Media types** in the Zabbix UI.
2. Click **Create media type**.
3. Set:
   - **Name**: `IDMEFv2 ALERT FORWARDER`
   - **Type**: `Webhook`
   - **Timeout**: `10s` (recommended)

### Step 2 – Add script code

Paste the following JavaScript code in the **Script** section:

```javascript
/*
 * Webhook “IDMEFv2 ALERT FORWARDER”
 * Sends Zabbix event ID as JSON to the configured connector endpoint.
 *
 * Required parameters (defined under the 'Parameters' tab):
 *   eventid → {EVENT.ID}
 *   url     → connector endpoint URL
 */

try {
    Zabbix.log(4, '[ IDMEFv2 ALERT FORWARDER ] Started with params: ' + value);

    const params = JSON.parse(value);          
    const req    = new HttpRequest();

    if (params.HTTPProxy) {
        req.setProxy(params.HTTPProxy);
    }

    req.addHeader('Content-Type: application/json');

    const payload = {
        eventid: params.eventid
    };

    const targetUrl = params.url || 'http://127.0.0.1:9090/alert';

    const resp = req.post(targetUrl, JSON.stringify(payload));

    if (req.getStatus() < 200 || req.getStatus() >= 300) {
        throw 'Request failed. HTTP ' + req.getStatus() + ' – Response: ' + resp;
    }

    return 'OK';

} catch (error) {
    Zabbix.log(3, '[ IDMEFv2 ALERT FORWARDER ] Error: ' + error);
    throw 'Failed with error: ' + error;
}
```

### Step 3 – Add Parameters

In the **Parameters** tab of the Media Type, add the following entries:

| Name     | Value                                 |
|----------|----------------------------------------|
| eventid  | `{EVENT.ID}`                          |
| url      | `http://127.0.0.1:9090/alert` |

> You can change the `url` to match your connector’s actual host, IP address, and port.

---

### Step 4 – Associate the Media Type with a User or Group

1. Go to **Users → Users**.
2. Click on the user you want to associate the media type with.
3. Open the **Media** tab and click **Add**.
4. In the **Type** field, select **IDMEFv2 ALERT FORWARDER**.
5. In the **Send to** field, enter the IDMEFv2 server URL.
6. Leave the other fields with their default values and ensure the media entry is enabled.
7. Click **Add** to add the media entry.
8. Click **Update** to save the edit.

---

### Step 5 – Use it in an Action

1. Go to **Alerts → Actions → Trigger actions**.
2. Create a new action or edit an existing one triggered by **problem events**.
3. Enter a descriptive **Name** for the action.
4. In the **Operations** tab, select the user (or user group) to whom you previously assigned the `IDMEFv2 ALERT FORWARDER` media type.
5. Add a step that sends a message using the `IDMEFv2 ALERT FORWARDER` by selecting it under **Send to media type**.
6. Select the **Custom message** checkbox and add a subject and message (The message won't work otherwise).
