

common_js = '''
document.addEventListener("DOMContentLoaded", function() {
    const errorBannerElement = document.querySelector('#errorbanner');
    const logError = e => {
        console.error(e);
        const p = document.createElement('p');
        p.classList.add('error');
        p.innerText = `${e}`;
        errorBannerElement.appendChild(p);
    };
    async function makeFetchResponseErrorMessage(response) {
        // const checkIfFormValidationError = async response => {
        //   if( response.status===415 ) {
        //     try {
        //       const data = await response.json();
        //       const errorMsg = data?.error;
        //       if( errorMsg )
        //         return `Validation failed: ${errorMsg}`;
        //     } catch(e) {
        //       // ok to ignore, if response is not json, or anything else - validation should anyway be caught earlier
        //     }
        //   }
        //   return null;
        // }
        if( response instanceof Promise )
          return makeFetchResponseErrorMessage(await response);
        else if( response instanceof Response ) {
          // const possibleFormValidationError = await checkIfFormValidationError(response);
          // if( possibleFormValidationError )
          //   return possibleFormValidationError;
          const prefix = `HTTP ${ response.status }`;
          try {
            const contentType = response.headers.get( 'content-type' ) || '';
            if( contentType.includes( 'application/json' ) ) {
              const body = await response.json();
              // Prefer a non-empty `error` field.
              if( body && !!body.error ) {
                return `${ prefix }: ${ body.error }`;
              }
              // Fall back to the whole JSON response.
              const details = JSON.stringify( body );
              return details ? `${ prefix }: ${ details }` : prefix;
            }
            // For text/plain and other non-JSON responses, use the response text.
            const text = await response.text();
            return text.trim() ? `${ prefix }: ${ text }` : prefix;
          } catch( e ) {
            // If the response body cannot be read/parsed, at least return the status.
            return prefix;
          }
        } else if( response instanceof Error ) {
          return `${response}`;
        } else {
          return `${response}`;
        }
    };
    const handleFormSubmit = async formElement=>{
        try {
            const url = formElement.getAttribute('action');
            const method = formElement.getAttribute('method');
            const body = new URLSearchParams(new FormData(formElement));
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body,
            });
            Array.from(formElement.querySelectorAll('[data-role="validation-error"]')).forEach(errBannerEl=>{errBannerEl.innerText = '';});
            if( response.status===415 ) {
                const data = await response.json()
                const errorMsg = data?.error;
                const errorPath = data?.path;
                if( errorMsg ) {
                    // <span data-role="validation-error" data-for="
                    const targetErrorPlaceholders = Array.from(formElement.querySelectorAll('[data-role="validation-error"][data-for="'+errorPath+'"]'));
                    if( targetErrorPlaceholders.length>0 ) {
                        targetErrorPlaceholders.forEach(errBannerEl=>{errBannerEl.innerText = errorMsg;});
                        return;
                    }
                }
            }
            if( !response.ok ) {
                const err_msg = new Error(await makeFetchResponseErrorMessage(response));
                throw err_msg;
            }
            const result = await response.text();
            const p = document.createElement('p');
            p.innerText = 'Response received. You can close this window now.';
            formElement.innerHTML = '<div class="done"></div>';
            formElement.appendChild(p);
            (new Promise(r=>setTimeout(100,r))).then(()=>{ window.close(); });
        } catch(e) {
            logError(e);
            throw e;
        }
    };
    Array.from(document.querySelectorAll('form')).forEach(formElement=>Promise.resolve(formElement).then(formElement=>formElement.addEventListener('submit',function(event){
        event.preventDefault();
        handleFormSubmit(formElement);
        return false;
    })));
})
'''
