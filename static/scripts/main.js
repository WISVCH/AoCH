/// insert child into parent
/// `parent` - the HTML element to insert the child into
/// `rank` - integer indicating the rank of the person
/// `child` - the element to insert (gotten from json request to AoC)
/// `moving` - bool indicating if the children should be moving
/// `today` - boolean for if it is individual for todays leaderboard
function insertIndividual(parent, rank, child, moving, today) {
    if (typeof child !== "object") return;

    let child_el = document.createElement("div");
    child_el.classList.add("individual");
    let rank_el = document.createElement("span");
    rank_el.textContent = rank.toString();
    let score = document.createElement("span");
    score.textContent = child.score.toString();
    let name = document.createElement("span");
    name.textContent =
        child.name == null || child.name == undefined ? "unknown" : child.name;

    child_el.appendChild(rank_el);
    child_el.appendChild(score);
    child_el.appendChild(name);
    if (today) {
        // element gets added to today leaderboard, thus contains timestamps when it has been handed in
        let star1 = document.createElement("span");
        let star2 = document.createElement("span");

        star1.textContent = child.star1 ? child.star1 : "-";
        star2.textContent = child.star2 ? child.star2 : "-";

        child_el.appendChild(star1);
        child_el.appendChild(star2);
    } else {
        // the element gets added to the total leaderboard
        let stars = document.createElement("span");
        let text = "";
        // child.stars is a list of 0, 1, or 2 where the number is the amount of stars gotten said day
        child.stars.forEach((star, index) => {
        // add all stars with their color
        now = new Date();
        let day = now.getDate();
        let month = now.getMonth() + 1;
        if (month != 12) {
            day = 25;
        }
        if (index == day - 1) {
            text += '<span class="star today ';
        } else {
            text += '<span class="star ';
        }
        if (star === 0) {
            text += "black";
        } else if (star === 1) {
            text += "silver";
        } else if (star === 2) {
            text += "gold";
        }
        text += '">★   </span>';
        });
        stars.innerHTML = text;
        stars.style.textAlign = "center";

        child_el.appendChild(stars);
    }
    if (moving) {
        if (parent.classList.contains("middle")) child_el.classList.add("move");
        child_el.addEventListener("animationiteration", cycleChildren);
    }
    parent.prepend(child_el);
}

/// This function is callped to input leaderboard statistics in a certain wrapper
/// - `selector` : this field is the id of the parentwrapper that will contain the children
/// - `children` : this field will contain all children that will be added to the parent (it should be an array)
/// - `today` : if the children will be added to the today leaderboard this is true
function render(selector, children, today) {
    let el = document.querySelector(selector);
    let max_in_list =
        ((el.parentNode.offsetHeight / screen.height) * 100) / 2.2;
    console.log(max_in_list);
    // remove all children as we will be adding them again
    el.innerHTML = "";
    // adding children
    if (children.length > max_in_list)
        insertIndividual(el, 1, children[0], true, today);
    for (let i = children.length - 1; i >= 0; i--) {
        let child = children[i];
        insertIndividual(
        el,
        i + 1,
        child,
        children.length > max_in_list,
        today
        );
    }
}

function cycleChildren() {
    let self = this;
    if (self.nextElementSibling) {
        self.innerHTML = self.nextElementSibling.innerHTML;
    } else {
        self.innerHTML = self.parentElement.firstElementChild.innerHTML;
    }
}

let step = 0;

function move_left(el) {
    el.classList.add("left");
    el.classList.remove("middle", "right");
    if (el.children[1].children.length > 0) {
        for (
        let i = 0;
        i < el.children[1].lastElementChild.children.length;
        i++
        ) {
        el.children[1].lastElementChild.children[i].classList.remove("move");
        }
    }
}

function move_middle(el) {
    el.classList.add("middle");
    el.classList.remove("right", "left");
    if (
        el.children[1].children.length > 0 &&
        ((el.children[1].offsetHeight / screen.height) * 100) / 2.2 <
        el.children[1].lastElementChild.children.length
    ) {
        for (
        let i = 0;
        i < el.children[1].lastElementChild.children.length;
        i++
        ) {
        if (!el.classList.contains("nomove"))
            el.children[1].lastElementChild.children[i].classList.add("move");
        }
    }
}

function move_right(el) {
    el.classList.add("right");
    el.classList.remove("middle");
    if (el.children[1].children.length > 0) {
        for (
        let i = 0;
        i < el.children[1].lastElementChild.children.length;
        i++
        ) {
        el.children[1].lastElementChild.children[i].classList.remove("move");
        }
    }
}

function swap(el) {
    let from = "left";
    let to = "right";
    if (el.classList.contains(to)) {
        from = "right";
        to = "left";
    }
    el.classList.remove("transition");
    setTimeout(() => {
        el.classList.remove(from);
        el.classList.add(to);
        setTimeout(() => {
        el.classList.add("transition");
        }, 100);
    }, 100);
}

function move(el, offset) {
    let cur_step = (step + offset) % 6;
    if (cur_step == 0) {
        move_left(el);
    } else if (cur_step == 1) {
        swap(el);
    } else if (cur_step == 2) {
        move_middle(el);
    } else if (cur_step == 3) {
        move_right(el);
    } else if (cur_step == 4) {
        swap(el);
    } else if (cur_step == 5) {
        move_middle(el);
    }
}

function transitions() {
    let l = document.querySelectorAll(".container > div")[2];
    let m = document.querySelectorAll(".container > div")[0];
    let r = document.querySelectorAll(".container > div")[1];

    move(l, 4);
    move(m, 0);
    move(r, 2);
    step = (step + 1) % 6;
}
