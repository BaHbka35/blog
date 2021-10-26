// let elements = document.querySelectorAll(".answer-button")

// bo = document.querySelectorAll("body")
// console.log(bo)

// for (elem of elements){
//     console.log(elem)
//     elem.onclik = function(event){
//         bo.style.backgroundColor = "red"
//     }
// }

// // function changeDisplay(id){
// //     // for (elem of elements){
// //     // elem.classList.add('seen')
// //     // }
// //     console.log(id)
// // }

function changeDisplay(idComment){
    console.log(idComment)
    elem = document.getElementById(idComment)
    console.log(elem)
    // elem.classList.remove("not-seen")
    // elem.classList.add('seen')
    elem.classList.toggle("seen")



    // but = document.querySelectorAll(".not-seen")
    // for (i of but){
    //     i.classList.add("seen")
    // }
    // elem.classList.add("not-seen")
    // but.classList.add("seen")
    // elem.style.color = "red"
    // console.log(elem)
}